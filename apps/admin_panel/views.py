"""
Admin panel API views.

All endpoints require is_staff=True (enforced by IsStaffUser permission).
All responses are pure JSON — no HTML pages.

Endpoints
---------
GET    /api/v1/admin/dashboard/           — stats snapshot
GET    /api/v1/admin/settings/            — get admin profile
PATCH  /api/v1/admin/settings/            — update admin profile (name, email, avatar)
GET    /api/v1/admin/orders/              — list all orders (filterable by status)
PATCH  /api/v1/admin/orders/<id>/status/  — update order status only
DELETE /api/v1/admin/orders/<id>/         — delete an order
GET    /api/v1/admin/projects/            — list all projects
POST   /api/v1/admin/projects/            — create a project
GET    /api/v1/admin/projects/<id>/       — retrieve a project
PATCH  /api/v1/admin/projects/<id>/       — update a project
DELETE /api/v1/admin/projects/<id>/       — delete a project
GET    /api/v1/admin/coupons/             — list all coupons
POST   /api/v1/admin/coupons/             — create a coupon
GET    /api/v1/admin/coupons/<id>/        — retrieve a coupon
PATCH  /api/v1/admin/coupons/<id>/        — update a coupon
DELETE /api/v1/admin/coupons/<id>/        — delete a coupon
"""

from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Q
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order
from apps.projects.models import Project, ProjectMedia
from apps.projects.serializers import ProjectMediaSerializer
from .models import Coupon
from .permissions import IsStaffUser
from .serializers import (
    AdminOrderSerializer,
    AdminOrderStatusSerializer,
    AdminProjectSerializer,
    AdminProjectCreateSerializer,
    AdminProjectUpdateSerializer,
    CouponSerializer,
    DashboardStatsSerializer,
    AdminSettingsSerializer,
    AdminSettingsUpdateSerializer,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class AdminDashboardView(APIView):
    """
    GET /api/v1/admin/dashboard/
    Returns a stats snapshot for the admin dashboard.
    """
    permission_classes = [IsStaffUser]

    def get(self, request):
        order_qs = Order.objects.all()

        stats = {
            "total_orders":       order_qs.count(),
            "total_revenue":      order_qs.aggregate(
                                      total=Sum("total_amount")
                                  )["total"] or 0,
            "pending_orders":     order_qs.filter(status=Order.Status.PENDING).count(),
            "confirmed_orders":   order_qs.filter(status=Order.Status.CONFIRMED).count(),
            "in_progress_orders": order_qs.filter(status=Order.Status.IN_PROGRESS).count(),
            "completed_orders":   order_qs.filter(status=Order.Status.DELIVERED).count(),
            "cancelled_orders":   order_qs.filter(status=Order.Status.CANCELLED).count(),
            "total_projects":     Project.objects.count(),
            "active_projects":    Project.objects.filter(status=Project.Status.ACTIVE).count(),
            "total_coupons":      Coupon.objects.count(),
            "active_coupons":     Coupon.objects.filter(is_active=True).count(),
            "total_users":        User.objects.count(),
        }

        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Admin Settings
# ---------------------------------------------------------------------------

class AdminSettingsView(APIView):
    """
    GET   /api/v1/admin/settings/  — retrieve the logged-in admin's profile
    PATCH /api/v1/admin/settings/  — update name, email, and/or avatar

    Accepts both application/json and multipart/form-data (for avatar uploads).
    Always returns JSON in the shape: { id, name, email, avatar, is_staff, is_superuser }
    """
    permission_classes = [IsStaffUser]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        serializer = AdminSettingsSerializer(
            request.user, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = AdminSettingsUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated_user = serializer.save()

        # Return the read serializer shape the frontend expects
        return Response(
            AdminSettingsSerializer(updated_user, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

class AdminOrderListView(generics.ListAPIView):
    """
    GET /api/v1/admin/orders/
    List all orders across all users.
    Optional query params:
      ?status=pending|confirmed|in_progress|delivered|cancelled
      ?search=<email or order id>
    """
    serializer_class   = AdminOrderSerializer
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        qs = Order.objects.select_related("client", "project").all()

        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(client__email__icontains=search) |
                Q(pk__icontains=search)
            )

        return qs


class AdminOrderStatusUpdateView(generics.UpdateAPIView):
    """
    PATCH /api/v1/admin/orders/<id>/status/
    Update only the status field of an order.
    """
    serializer_class   = AdminOrderStatusSerializer
    permission_classes = [IsStaffUser]
    queryset           = Order.objects.all()
    http_method_names  = ["patch", "options", "head"]

    def partial_update(self, request, *args, **kwargs):
        instance   = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Return the full order after update
        return Response(
            AdminOrderSerializer(instance, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class AdminOrderDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/v1/admin/orders/<id>/
    Permanently delete an order.
    """
    permission_classes = [IsStaffUser]
    queryset           = Order.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"detail": "Order deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

class AdminProjectListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/admin/projects/  — list all projects
    POST /api/v1/admin/projects/  — create a project (admin assigns owner)
    """
    permission_classes = [IsStaffUser]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdminProjectCreateSerializer
        return AdminProjectSerializer

    def get_queryset(self):
        qs = Project.objects.select_related("owner").all()

        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(owner__email__icontains=search)
            )

        return qs

    def create(self, request, *args, **kwargs):
        serializer = AdminProjectCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        return Response(
            AdminProjectSerializer(project, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class AdminProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/admin/projects/<id>/  — retrieve
    PATCH  /api/v1/admin/projects/<id>/  — update (title, description, status, thumbnail, owner)
    DELETE /api/v1/admin/projects/<id>/  — delete
    """
    permission_classes = [IsStaffUser]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]
    queryset           = Project.objects.select_related("owner").all()
    http_method_names  = ["get", "patch", "delete", "options", "head"]

    def get_serializer_class(self):
        return AdminProjectSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Use the dedicated write serializer — it has a real ImageField for thumbnail
        serializer = AdminProjectUpdateSerializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance.refresh_from_db()
        # Return the read serializer so thumbnail comes back as an absolute URL
        return Response(
            AdminProjectSerializer(instance, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"detail": "Project deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Coupons
# ---------------------------------------------------------------------------

class AdminCouponListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/admin/coupons/  — list all coupons
    POST /api/v1/admin/coupons/  — create a coupon
    Accepts application/json only (no file uploads for coupons).
    """
    serializer_class   = CouponSerializer
    permission_classes = [IsStaffUser]
    parser_classes     = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        qs = Coupon.objects.all()

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )

        return qs


class AdminCouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/admin/coupons/<id>/  — retrieve
    PATCH  /api/v1/admin/coupons/<id>/  — partial update (only sent fields change)
    DELETE /api/v1/admin/coupons/<id>/  — delete
    """
    serializer_class   = CouponSerializer
    permission_classes = [IsStaffUser]
    queryset           = Coupon.objects.all()
    parser_classes     = [JSONParser, MultiPartParser, FormParser]
    http_method_names  = ["get", "patch", "delete", "options", "head"]

    def partial_update(self, request, *args, **kwargs):
        instance   = self.get_object()
        serializer = CouponSerializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance.refresh_from_db()
        return Response(
            CouponSerializer(instance, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"detail": "Coupon deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Project Media
# ---------------------------------------------------------------------------

class AdminProjectMediaView(generics.ListCreateAPIView):
    """
    GET  /api/v1/admin/projects/<project_pk>/media/  — list media for a project
    POST /api/v1/admin/projects/<project_pk>/media/  — upload a new media item
    Accepts multipart/form-data (file upload) or JSON (url-based media).
    """
    serializer_class   = ProjectMediaSerializer
    permission_classes = [IsStaffUser]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return ProjectMedia.objects.filter(project_id=self.kwargs["project_pk"])

    def perform_create(self, serializer):
        project = generics.get_object_or_404(Project, pk=self.kwargs["project_pk"])
        serializer.save(project=project)


class AdminProjectMediaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/admin/projects/<project_pk>/media/<pk>/  — retrieve
    PATCH  /api/v1/admin/projects/<project_pk>/media/<pk>/  — update (reorder, set featured)
    DELETE /api/v1/admin/projects/<project_pk>/media/<pk>/  — delete file + record
    """
    serializer_class   = ProjectMediaSerializer
    permission_classes = [IsStaffUser]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]
    http_method_names  = ["get", "patch", "delete", "options", "head"]

    def get_queryset(self):
        return ProjectMedia.objects.filter(project_id=self.kwargs["project_pk"])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Delete the actual file from disk
        if instance.file:
            try:
                instance.file.delete(save=False)
            except Exception:
                pass
        instance.delete()
        return Response({"detail": "Media deleted."}, status=status.HTTP_200_OK)
