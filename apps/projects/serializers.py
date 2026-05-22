from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source="owner.email")

    class Meta:
        model = Project
        fields = (
            "id",
            "owner",
            "owner_email",
            "title",
            "description",
            "status",
            "thumbnail",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "owner", "owner_email", "created_at", "updated_at")
