from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "project", "status", "total_amount", "created_at")
    list_filter = ("status",)
    search_fields = ("client__email", "project__title")
    ordering = ("-created_at",)
