from rest_framework import serializers
from .models import Project, ProjectMedia


# ---------------------------------------------------------------------------
# Media
# ---------------------------------------------------------------------------

class ProjectMediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model  = ProjectMedia
        fields = (
            "id", "media_type", "file", "file_url",
            "url", "is_featured", "order", "created_at",
        )
        read_only_fields = ("id", "created_at", "file_url")
        extra_kwargs = {
            "file": {"required": False, "allow_null": True},
            "url":  {"required": False, "allow_blank": True},
        }

    def get_file_url(self, obj):
        if not obj.file:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url


# ---------------------------------------------------------------------------
# Project — read (full detail returned to frontend)
# ---------------------------------------------------------------------------

class ProjectSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source="owner.email")
    thumbnail   = serializers.SerializerMethodField()
    media       = ProjectMediaSerializer(many=True, read_only=True)
    status_display   = serializers.ReadOnlyField(source="get_status_display")
    category_display = serializers.ReadOnlyField(source="get_category_display")
    level_display    = serializers.ReadOnlyField(source="get_level_display")
    badge_display    = serializers.ReadOnlyField(source="get_badge_display")

    class Meta:
        model = Project
        fields = (
            "id",
            "owner",
            "owner_email",
            # Basic info
            "title",
            "category",          "category_display",
            "level",             "level_display",
            "delivery_time",
            "badge",             "badge_display",
            "short_description",
            "description",
            # Pricing
            "sale_price",
            "original_price",
            "price",
            # Tech & features
            "technologies",
            "key_features",
            "whats_included",
            # Media
            "thumbnail",
            "demo_video_url",
            "media",
            # Links
            "project_links",
            # Visibility
            "status",            "status_display",
            "is_sold_out",
            # Timestamps
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id", "owner", "owner_email",
            "status_display", "category_display", "level_display", "badge_display",
            "created_at", "updated_at",
        )

    def get_thumbnail(self, obj):
        if not obj.thumbnail:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return obj.thumbnail.url


# ---------------------------------------------------------------------------
# Project — write (POST / PATCH)
# ---------------------------------------------------------------------------

class ProjectWriteSerializer(serializers.ModelSerializer):
    """
    Accepts all editable fields including file uploads.
    All fields optional for PATCH (partial=True).
    JSON array fields (technologies, key_features, etc.) accept either
    a real JSON array or a comma-separated string for FormData compatibility.
    """

    class Meta:
        model = Project
        fields = (
            "title",
            "category",
            "level",
            "delivery_time",
            "badge",
            "short_description",
            "description",
            "sale_price",
            "original_price",
            "price",
            "technologies",
            "key_features",
            "whats_included",
            "thumbnail",
            "demo_video_url",
            "project_links",
            "status",
            "is_sold_out",
        )
        extra_kwargs = {
            "title":             {"required": False},
            "category":          {"required": False},
            "level":             {"required": False},
            "delivery_time":     {"required": False, "allow_blank": True},
            "badge":             {"required": False, "allow_blank": True},
            "short_description": {"required": False, "allow_blank": True},
            "description":       {"required": False, "allow_blank": True},
            "sale_price":        {"required": False, "allow_null": True},
            "original_price":    {"required": False, "allow_null": True},
            "price":             {"required": False, "allow_null": True},
            "technologies":      {"required": False},
            "key_features":      {"required": False},
            "whats_included":    {"required": False},
            "thumbnail":         {"required": False, "allow_null": True},
            "demo_video_url":    {"required": False, "allow_blank": True},
            "project_links":     {"required": False},
            "status":            {"required": False, "default": "active"},
            "is_sold_out":       {"required": False},
        }

    def _parse_json_field(self, value):
        """
        Accept either a real list (from JSON body) or a JSON string
        (from FormData where arrays are serialized as strings).
        """
        import json
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except (ValueError, TypeError):
                # Treat as comma-separated string
                return [v.strip() for v in value.split(",") if v.strip()]
        return []

    def validate_technologies(self, value):
        return self._parse_json_field(value)

    def validate_key_features(self, value):
        return self._parse_json_field(value)

    def validate_whats_included(self, value):
        return self._parse_json_field(value)

    def validate_project_links(self, value):
        import json
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except (ValueError, TypeError):
                pass
        return []
