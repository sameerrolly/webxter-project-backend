"""
Serializers for the admin panel.
All serializers expose clean JSON — no HTML, no nested HTML forms.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.orders.models import Order
from apps.projects.models import Project, ProjectMedia
from apps.projects.serializers import ProjectMediaSerializer, ProjectWriteSerializer
from .models import Coupon

User = get_user_model()


# ---------------------------------------------------------------------------
# Admin Settings
# ---------------------------------------------------------------------------

class AdminSettingsSerializer(serializers.ModelSerializer):
    name   = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ("id", "name", "email", "avatar", "is_staff", "is_superuser")
        read_only_fields = ("id", "is_staff", "is_superuser")

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email

    def get_avatar(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url


class AdminSettingsUpdateSerializer(serializers.ModelSerializer):
    name  = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False)

    class Meta:
        model  = User
        fields = ("name", "email", "avatar")
        extra_kwargs = {"avatar": {"required": False, "allow_null": True}}

    def validate_email(self, value):
        value = value.lower().strip()
        if self.instance and self.instance.email == value:
            return value
        if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def update(self, instance, validated_data):
        name = validated_data.pop("name", None)
        if name is not None:
            parts = name.strip().split(" ", 1)
            instance.first_name = parts[0]
            instance.last_name  = parts[1] if len(parts) > 1 else ""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

class AdminOrderSerializer(serializers.ModelSerializer):
    client_email   = serializers.ReadOnlyField(source="client.email")
    client_name    = serializers.SerializerMethodField()
    project_title  = serializers.ReadOnlyField(source="project.title")
    status_display = serializers.ReadOnlyField(source="get_status_display")

    class Meta:
        model  = Order
        fields = (
            "id", "client", "client_email", "client_name",
            "project", "project_title",
            "status", "status_display",
            "total_amount", "notes",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "client", "client_email", "client_name",
            "project_title", "status_display", "created_at", "updated_at",
        )

    def get_client_name(self, obj):
        return f"{obj.client.first_name} {obj.client.last_name}".strip() or obj.client.email


class AdminOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Order
        fields = ("id", "status")
        read_only_fields = ("id",)

    def validate_status(self, value):
        valid = [c[0] for c in Order.Status.choices]
        if value not in valid:
            raise serializers.ValidationError(f"Choose from: {', '.join(valid)}")
        return value


# ---------------------------------------------------------------------------
# Projects — READ serializer (full detail, absolute URLs)
# ---------------------------------------------------------------------------

class AdminProjectSerializer(serializers.ModelSerializer):
    """Full read serializer — returned after every create/update."""
    owner_email      = serializers.ReadOnlyField(source="owner.email")
    owner_name       = serializers.SerializerMethodField()
    status_display   = serializers.ReadOnlyField(source="get_status_display")
    category_display = serializers.ReadOnlyField(source="get_category_display")
    level_display    = serializers.ReadOnlyField(source="get_level_display")
    badge_display    = serializers.ReadOnlyField(source="get_badge_display")
    thumbnail        = serializers.SerializerMethodField()
    media            = ProjectMediaSerializer(many=True, read_only=True)

    class Meta:
        model  = Project
        fields = (
            "id", "owner", "owner_email", "owner_name",
            # Basic info
            "title",
            "category",          "category_display",
            "level",             "level_display",
            "delivery_time",
            "badge",             "badge_display",
            "short_description",
            "description",
            # Pricing
            "sale_price", "original_price", "price",
            # Tech & features
            "technologies", "key_features", "whats_included",
            # Media
            "thumbnail", "demo_video_url", "media",
            # Links
            "project_links",
            # Visibility
            "status", "status_display", "is_sold_out",
            # Timestamps
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "owner_email", "owner_name",
            "status_display", "category_display", "level_display", "badge_display",
            "created_at", "updated_at",
        )

    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}".strip() or obj.owner.email

    def get_thumbnail(self, obj):
        if not obj.thumbnail:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.thumbnail.url) if request else obj.thumbnail.url


# ---------------------------------------------------------------------------
# Projects — WRITE serializers (reuse from apps.projects)
# ---------------------------------------------------------------------------

class AdminProjectCreateSerializer(ProjectWriteSerializer):
    """
    POST /api/v1/admin/projects/
    Extends ProjectWriteSerializer with optional owner assignment.
    Defaults owner to the logged-in admin.
    """
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        help_text="User ID. Defaults to the logged-in admin.",
    )

    class Meta(ProjectWriteSerializer.Meta):
        fields = ("owner",) + ProjectWriteSerializer.Meta.fields

    def create(self, validated_data):
        if "owner" not in validated_data:
            request = self.context.get("request")
            if request and request.user.is_authenticated:
                validated_data["owner"] = request.user
        return super().create(validated_data)


class AdminProjectUpdateSerializer(ProjectWriteSerializer):
    """PATCH /api/v1/admin/projects/<id>/ — all fields optional."""
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
    )

    class Meta(ProjectWriteSerializer.Meta):
        fields = ("owner",) + ProjectWriteSerializer.Meta.fields


# ---------------------------------------------------------------------------
# Coupons
# ---------------------------------------------------------------------------

class CouponSerializer(serializers.ModelSerializer):
    is_exhausted     = serializers.ReadOnlyField()
    discount_display = serializers.SerializerMethodField()

    class Meta:
        model  = Coupon
        fields = (
            "id", "code", "description",
            "discount_type", "discount_value", "min_order_amount",
            "max_uses", "used_count",
            "is_active", "is_exhausted", "discount_display",
            "valid_from", "valid_until",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "used_count", "is_exhausted", "created_at", "updated_at")
        extra_kwargs = {
            "discount_type":    {"required": False},
            "min_order_amount": {"required": False},
            "max_uses":         {"required": False, "allow_null": True},
            "is_active":        {"required": False},
            "description":      {"required": False, "allow_blank": True},
            "valid_from":       {"required": False},
            "valid_until":      {"required": False},
            "discount_value":   {"required": False},
        }

    def get_discount_display(self, obj):
        if obj.discount_type == Coupon.DiscountType.PERCENTAGE:
            return f"{obj.discount_value}% off"
        return f"₹{obj.discount_value} off"

    def validate(self, attrs):
        valid_from  = attrs.get("valid_from",  getattr(self.instance, "valid_from",  None))
        valid_until = attrs.get("valid_until", getattr(self.instance, "valid_until", None))
        if valid_from and valid_until and valid_from >= valid_until:
            raise serializers.ValidationError({"valid_until": "valid_until must be after valid_from."})
        discount_type  = attrs.get("discount_type",  getattr(self.instance, "discount_type",  None))
        discount_value = attrs.get("discount_value", getattr(self.instance, "discount_value", None))
        if discount_type == Coupon.DiscountType.PERCENTAGE and discount_value is not None:
            if discount_value > 100:
                raise serializers.ValidationError({"discount_value": "Percentage cannot exceed 100."})
        return attrs


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class DashboardStatsSerializer(serializers.Serializer):
    total_orders       = serializers.IntegerField()
    total_revenue      = serializers.DecimalField(max_digits=14, decimal_places=2)
    pending_orders     = serializers.IntegerField()
    confirmed_orders   = serializers.IntegerField()
    in_progress_orders = serializers.IntegerField()
    completed_orders   = serializers.IntegerField()
    cancelled_orders   = serializers.IntegerField()
    total_projects     = serializers.IntegerField()
    active_projects    = serializers.IntegerField()
    total_coupons      = serializers.IntegerField()
    active_coupons     = serializers.IntegerField()
    total_users        = serializers.IntegerField()
