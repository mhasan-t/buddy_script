from datetime import datetime, timezone as dt_timezone

from django.conf import settings
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import RefreshTokenRecord
from ..serializers import (
    UserSerializer,
    UserRegistrationSerializer,
)


def set_jwt_cookies(response, refresh_token, access_token):
    """Helper function to set JWT tokens as HTTP-only cookies"""
    response.set_cookie(
        key="refresh_token",
        value=str(refresh_token),
        max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
        httponly=True,
        secure=not settings.DEBUG,  # Only secure in production
        samesite="Lax",
        path="/",
    )
    response.set_cookie(
        key="access_token",
        value=str(access_token),
        max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        path="/",
    )
    return response


def _build_refresh_token_record(refresh_token, user, device_info=None):
    return RefreshTokenRecord.objects.create(
        user=user,
        jti=str(refresh_token["jti"]),
        expires_at=datetime.fromtimestamp(refresh_token["exp"], tz=dt_timezone.utc),
        device_info=device_info,
    )


def _get_refresh_token_record(refresh_token):
    record = RefreshTokenRecord.objects.filter(
        jti=str(refresh_token["jti"]), revoked=False
    ).first()
    if record is None:
        raise InvalidToken("Refresh token is invalid or revoked")
    if record.expires_at <= timezone.now():
        raise InvalidToken("Refresh token has been revoked or expired")
    return record


def _rotate_refresh_token(refresh_token_str, device_info=None):
    refresh = RefreshToken(refresh_token_str)
    record = _get_refresh_token_record(refresh)
    record.revoked = True
    record.save(update_fields=["revoked"])

    new_refresh = RefreshToken.for_user(record.user)
    _build_refresh_token_record(new_refresh, record.user, device_info=device_info)
    return new_refresh, new_refresh.access_token


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            # Generate tokens for the newly created user
            user = self.get_serializer().instance
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            device_info = request.META.get("HTTP_USER_AGENT", "")
            _build_refresh_token_record(refresh, user, device_info=device_info)

            # Set cookies instead of returning tokens in response
            response = set_jwt_cookies(response, refresh, access)
        return response


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from django.contrib.auth import authenticate

        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Authenticate using email instead of username
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        device_info = request.META.get("HTTP_USER_AGENT", "")
        _build_refresh_token_record(refresh, user, device_info=device_info)

        response = Response(
            {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            },
            status=status.HTTP_200_OK,
        )
        return set_jwt_cookies(response, refresh, access)


class RefreshTokenView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "Refresh token not found in cookies"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            device_info = request.META.get("HTTP_USER_AGENT", "")
            new_refresh, access = _rotate_refresh_token(
                refresh_token, device_info=device_info
            )
            response = Response(
                {"success": "Token refreshed"}, status=status.HTTP_200_OK
            )
            return set_jwt_cookies(response, new_refresh, access)
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except InvalidToken as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "Refresh token not found in cookies"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(refresh_token)
            record = RefreshTokenRecord.objects.filter(
                jti=str(refresh["jti"]), revoked=False
            ).first()
            if record is not None:
                record.revoked = True
                record.save(update_fields=["revoked"])
        except TokenError:
            pass

        response = Response(
            {"success": "Logged out successfully"}, status=status.HTTP_200_OK
        )
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")
        return response


class LogoutAllView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "Refresh token not found in cookies"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(refresh_token)
            record = RefreshTokenRecord.objects.filter(
                jti=str(refresh["jti"]), revoked=False
            ).first()
            if record is None:
                raise InvalidToken("Refresh token is invalid or revoked")

            RefreshTokenRecord.objects.filter(user=record.user, revoked=False).update(
                revoked=True
            )
        except (TokenError, InvalidToken) as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response(
            {"success": "Logged out from all devices"}, status=status.HTTP_200_OK
        )
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")
        return response


class UserMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
