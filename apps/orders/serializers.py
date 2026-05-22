from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    client_email = serializers.ReadOnlyField(source="client.email")
    project_title = serializers.ReadOnlyField(source="project.title")

    class Meta:
        model = Order
        fields = (
            "id",
            "client",
            "client_email",
            "project",
            "project_title",
            "status",
            "total_amount",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "client", "client_email", "project_title", "created_at", "updated_at")
