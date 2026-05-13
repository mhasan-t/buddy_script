from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
from ..serializers import (
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
            refresh = RefreshToken(refresh_token)
            access = refresh.access_token

            response = Response(
                {"success": "Token refreshed"}, status=status.HTTP_200_OK
            )
            return set_jwt_cookies(response, refresh, access)
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        response = Response(
            {"success": "Logged out successfully"}, status=status.HTTP_200_OK
        )
        # Clear cookies
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")
        return response
