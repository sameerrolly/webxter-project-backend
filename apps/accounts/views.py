"""
JWT Authentication views for the accounts app.

Endpoints
---------
POST   /api/v1/auth/register/          — create account, returns tokens + user
POST   /api/v1/auth/login/             — login, returns tokens + user
POST   /api/v1/auth/token/refresh/     — rotate refresh token, returns new access
POST   /api/v1/auth/token/verify/      — verify an access token, returns decoded user
POST   /api/v1/auth/logout/            — blacklist refresh token
GET    /api/v1/auth/me/                — return current user from token (protected)
GET    /api/v1/auth/profile/           — full profile (protected)
PATCH  /api/v1/auth/profile/           — update profile (protected)
PATCH  /api/v1/auth/avatar/            — upload / replace avatar image (protected)
POST   /api/v1/auth/change-password/   — change password (protected)
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    TokenVerifySerializer,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

class RegisterView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register/
    Public. Creates a new user and immediately returns JWT tokens.

    Request body:
        email, first_name, last_name, password, password2

    Response 201:
        { message, user: {...}, tokens: { access, refresh } }
    """
    serializer_class   = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        # Embed custom claims
        refresh["email"]     = user.email
        refresh["full_name"] = user.full_name
        refresh["is_staff"]  = user.is_staff

        return Response(
            {
                "message": "Account created successfully.",
                "user": UserProfileSerializer(user, context={"request": request}).data,
                "tokens": {
                    "access":  str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class LoginView(TokenObtainPairView):
    """
    POST /api/v1/auth/login/
    Public. Authenticates user and returns JWT tokens + user profile.

    Request body:
        { email, password }

    Response 200:
        { access, refresh, user: {...} }
    """
    serializer_class   = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


# ---------------------------------------------------------------------------
# Token Refresh
# ---------------------------------------------------------------------------

class TokenRefreshView(TokenRefreshView):
    """
    POST /api/v1/auth/token/refresh/
    Public. Accepts a valid refresh token, returns a new access token.
    With ROTATE_REFRESH_TOKENS=True, also returns a new refresh token.

    Request body:
        { refresh }

    Response 200:
        { access, refresh }
    """
    permission_classes = [AllowAny]


# ---------------------------------------------------------------------------
# Token Verify
# ---------------------------------------------------------------------------

class TokenVerifyView(APIView):
    """
    POST /api/v1/auth/token/verify/
    Public. Verifies an access token and returns the decoded user payload.

    Request body:
        { token }

    Response 200:
        { valid: true, user_id, email, full_name, is_staff, exp }
    Response 401:
        { valid: false, detail: "..." }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"valid": False, "detail": serializer.errors["token"][0]},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            token = AccessToken(serializer.validated_data["token"])
            return Response(
                {
                    "valid":     True,
                    "user_id":   token["user_id"],
                    "email":     token.get("email", ""),
                    "full_name": token.get("full_name", ""),
                    "is_staff":  token.get("is_staff", False),
                    "exp":       token["exp"],
                },
                status=status.HTTP_200_OK,
            )
        except TokenError as e:
            return Response(
                {"valid": False, "detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    Protected. Blacklists the provided refresh token so it can't be reused.

    Request body:
        { refresh }

    Response 200:
        { message: "Logged out successfully." }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logged out successfully."},
                status=status.HTTP_200_OK,
            )
        except TokenError:
            return Response(
                {"detail": "Token is invalid or already expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ---------------------------------------------------------------------------
# Me  (lightweight — just returns user from the token, no DB hit)
# ---------------------------------------------------------------------------

class MeView(APIView):
    """
    GET /api/v1/auth/me/
    Protected. Returns the authenticated user's profile from the database.
    Useful for bootstrapping the frontend on page load.

    Response 200:
        { id, email, first_name, last_name, full_name, avatar, bio, is_staff, date_joined }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/v1/auth/profile/  — retrieve full profile
    PATCH /api/v1/auth/profile/  — update first_name, last_name, bio, avatar

    Accepts multipart/form-data (for file uploads) and application/json.
    """
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]
    http_method_names  = ["get", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return UpdateProfileSerializer
        return UserProfileSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UpdateProfileSerializer(
            instance,
            data=request.data,
            partial=True,
            context={"request": request},   # needed for validate_email self-exclusion
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Re-fetch from DB to get the latest state, then return full profile
        instance.refresh_from_db()
        return Response(
            UserProfileSerializer(instance, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Avatar Upload
# ---------------------------------------------------------------------------

class AvatarUploadView(APIView):
    """
    PATCH /api/v1/auth/avatar/
    Upload or replace the user's avatar image.

    Request:  multipart/form-data  { avatar: <image file> }
    Response: full UserProfile JSON with absolute avatar URL
    """
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def patch(self, request):
        if "avatar" not in request.FILES:
            return Response(
                {"detail": "No image file provided. Send the file under the 'avatar' key."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user

        # Delete old file from disk before saving new one
        if user.avatar:
            try:
                user.avatar.delete(save=False)
            except Exception:
                pass

        user.avatar = request.FILES["avatar"]
        user.save(update_fields=["avatar"])
        user.refresh_from_db()

        return Response(
            UserProfileSerializer(user, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Avatar Remove
# ---------------------------------------------------------------------------

class AvatarRemoveView(APIView):
    """
    DELETE /api/v1/auth/avatar/
    Remove the user's avatar — deletes the file from disk and clears the DB field.

    Response: full UserProfile JSON with avatar: null
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user

        if not user.avatar:
            return Response(
                {"detail": "No avatar to remove."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Delete file from disk
        try:
            user.avatar.delete(save=False)
        except Exception:
            pass

        # Clear the DB field
        user.avatar = None
        user.save(update_fields=["avatar"])
        user.refresh_from_db()

        return Response(
            UserProfileSerializer(user, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Change Password
# ---------------------------------------------------------------------------

class ChangePasswordView(APIView):
    """
    POST /api/v1/auth/change-password/
    Protected. Validates old password before setting the new one.

    Request body:
        { old_password, new_password, new_password2 }

    Response 200:
        { message: "Password changed successfully." }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )
