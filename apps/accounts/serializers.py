"""
Serializers for the accounts app.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, TokenError

User = get_user_model()


# ---------------------------------------------------------------------------
# JWT — custom claims + user payload in login response
# ---------------------------------------------------------------------------

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the default login serializer to:
      - Embed email, full_name, is_staff inside the JWT payload
      - Return user profile data alongside the tokens in the response body
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Custom claims embedded in the token itself
        token["email"]     = user.email
        token["full_name"] = user.full_name
        token["is_staff"]  = user.is_staff
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Attach full user profile to the response body (not inside the token)
        # Pass request context so avatar returns an absolute URL
        request = self.context.get("request")
        data["user"] = UserProfileSerializer(self.user, context={"request": request}).data
        return data


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label="Confirm password",
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password", "password2")
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name":  {"required": False},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)


# ---------------------------------------------------------------------------
# Profile — read
# ---------------------------------------------------------------------------

class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "avatar",
            "bio",
            "is_staff",
            "date_joined",
        )
        read_only_fields = ("id", "email", "is_staff", "date_joined", "full_name")

    def get_avatar(self, obj):
        """Return an absolute URL so the frontend can use it directly."""
        if not obj.avatar:
            return None
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(obj.avatar.url)
        # Fallback: return the relative URL if no request in context
        return obj.avatar.url


# ---------------------------------------------------------------------------
# Profile — update
# ---------------------------------------------------------------------------

class UpdateProfileSerializer(serializers.ModelSerializer):
    """
    Allows updating profile fields including email.
    Email uniqueness check excludes the current user so saving the same
    email does not trigger a false "already exists" error.
    """
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "bio", "avatar", "email")
        extra_kwargs = {
            "first_name": {"required": False, "allow_blank": True},
            "last_name":  {"required": False, "allow_blank": True},
            "bio":        {"required": False, "allow_blank": True},
            "avatar":     {"required": False, "allow_null": True},
        }

    def validate_email(self, value):
        value = value.lower().strip()
        # Same email as current user — no change, skip uniqueness check
        if self.instance and self.instance.email == value:
            return value
        # Different email — ensure no other user owns it
        if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


# ---------------------------------------------------------------------------
# Change password
# ---------------------------------------------------------------------------

class ChangePasswordSerializer(serializers.Serializer):
    old_password  = serializers.CharField(required=True, write_only=True)
    new_password  = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password": "Passwords do not match."})
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


# ---------------------------------------------------------------------------
# Token verify — decode and return user info from an access token
# ---------------------------------------------------------------------------

class TokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

    def validate_token(self, value):
        try:
            AccessToken(value)
        except TokenError as e:
            raise serializers.ValidationError(str(e))
        return value
