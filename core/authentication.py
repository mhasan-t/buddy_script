# For Django 3.0+, we need the translation function
try:
    from django.utils.translation import gettext_lazy as _
except ImportError:
    from django.utils.translation import ugettext_lazy as _

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.exceptions import AuthenticationFailed


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads tokens from HTTP-only cookies
    instead of the Authorization header.
    """

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if valid JWT in cookies,
        otherwise returns `None`.
        """
        # Try to get the token from cookies
        raw_token = request.COOKIES.get("access_token")

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except InvalidToken:
            raise AuthenticationFailed("Invalid or expired token in cookie")
