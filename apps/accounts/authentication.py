"""
Custom JWT authentication backend.

Extends simplejwt's default to support:
  - Bearer token from Authorization header  (standard)
  - Token from HttpOnly cookie              (optional, more secure for web)

Cookie auth is disabled by default. Enable it by setting
JWT_AUTH_COOKIE = True in settings.py and sending the token
in a cookie named 'access_token'.
"""

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed


class CookieOrHeaderJWTAuthentication(JWTAuthentication):
    """
    Tries Authorization  header first, then falls back to HttpOnly cookie.
    This lets you support both React (header) and SSR (cookie) clients.
    """

    def authenticate(self, request):
        # 1. Try the standard Authorization: Bearer <token> header
        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)
            if raw_token is not None:
                try:
                    validated_token = self.get_validated_token(raw_token)
                    return self.get_user(validated_token), validated_token
                except TokenError as e:
                    raise InvalidToken(e.args[0])

        # 2. Fall back to HttpOnly cookie (opt-in via settings)     
        cookie_name = getattr(settings, "JWT_AUTH_COOKIE", None)
        if cookie_name:
            raw_token = request.COOKIES.get(cookie_name)
            if raw_token:
                try:
                    validated_token = self.get_validated_token(raw_token.encode())
                    return self.get_user(validated_token), validated_token
                except TokenError as e:
                    raise AuthenticationFailed(str(e))

        return None
