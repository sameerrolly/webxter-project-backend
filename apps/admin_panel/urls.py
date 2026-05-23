"""
URL patterns for the admin panel API.
Mounted at: /api/v1/admin/

All routes require is_staff=True.

GET    dashboard/                — stats snapshot
GET    settings/                 — get admin profile
PATCH  settings/                 — update admin profile (name, email, avatar)
GET    orders/                   — list all orders
PATCH  orders/<id>/status/       — update order status
DELETE orders/<id>/              — delete order
GET    projects/                 — list all projects
POST   projects/                 — create project
GET    projects/<id>/            — retrieve project
PATCH  projects/<id>/            — update project
DELETE projects/<id>/            — delete project
GET    coupons/                  — list all coupons
POST   coupons/                  — create coupon
GET    coupons/<id>/             — retrieve coupon
PATCH  coupons/<id>/             — update coupon
DELETE coupons/<id>/             — delete coupon
"""

from django.urls import path
from .views import (
    AdminDashboardView,
    AdminSettingsView,
    AdminOrderListView,
    AdminOrderStatusUpdateView,
    AdminOrderDeleteView,
    AdminProjectListCreateView,
    AdminProjectDetailView,
    AdminProjectMediaView,
    AdminProjectMediaDetailView,
    AdminCouponListCreateView,
    AdminCouponDetailView,
)

app_name = "admin_panel"

urlpatterns = [
    # Dashboard
    path("dashboard/",                              AdminDashboardView.as_view(),          name="dashboard"),

    # Settings
    path("settings/",                               AdminSettingsView.as_view(),            name="settings"),

    # Orders
    path("orders/",                                 AdminOrderListView.as_view(),           name="order_list"),
    path("orders/<int:pk>/status/",                 AdminOrderStatusUpdateView.as_view(),   name="order_status"),
    path("orders/<int:pk>/",                        AdminOrderDeleteView.as_view(),         name="order_delete"),

    # Projects
    path("projects/",                               AdminProjectListCreateView.as_view(),   name="project_list_create"),
    path("projects/<int:pk>/",                      AdminProjectDetailView.as_view(),       name="project_detail"),

    # Project media gallery
    path("projects/<int:project_pk>/media/",        AdminProjectMediaView.as_view(),        name="project_media_list"),
    path("projects/<int:project_pk>/media/<int:pk>/", AdminProjectMediaDetailView.as_view(), name="project_media_detail"),

    # Coupons
    path("coupons/",                                AdminCouponListCreateView.as_view(),    name="coupon_list_create"),
    path("coupons/<int:pk>/",                       AdminCouponDetailView.as_view(),        name="coupon_detail"),
]
