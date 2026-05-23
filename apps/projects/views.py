"""
Project endpoints.

GET  /api/v1/projects/       — public catalogue, no auth required
                               Shows all non-archived projects (draft, active, completed)
POST /api/v1/projects/       — create a project (auth required)
GET  /api/v1/projects/<id>/  — public, no auth required
PATCH/DELETE                 — auth required, owner or staff only
"""

from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from .models import Project
from .serializers import ProjectSerializer, ProjectWriteSerializer


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """GET/HEAD/OPTIONS open to all. Write methods require auth."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)


def _public_queryset():
    """
    Public project catalogue — everything except archived.
    draft = available for order, active = in progress, completed = done.
    Only archived projects are hidden from the public.
    """
    return Project.objects.select_related("owner").exclude(
        status=Project.Status.ARCHIVED
    )


class ProjectListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/projects/  — public catalogue (all non-archived projects)
    POST /api/v1/projects/  — create project (auth required)
    Accepts multipart/form-data so thumbnail file uploads work.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProjectWriteSerializer
        return ProjectSerializer

    def get_queryset(self):
        # Staff see everything including archived
        user = self.request.user
        if user and user.is_authenticated and user.is_staff:
            return Project.objects.select_related("owner").all()
        # Public and regular users see all non-archived
        return _public_queryset()

    def create(self, request, *args, **kwargs):
        serializer = ProjectWriteSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        project = serializer.save(owner=request.user)
        return Response(
            ProjectSerializer(project, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/projects/<id>/  — public
    PATCH  /api/v1/projects/<id>/  — auth required, owner or staff
    DELETE /api/v1/projects/<id>/  — auth required, owner or staff
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        return ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        # Write operations — owner or staff only
        if self.request.method not in permissions.SAFE_METHODS:
            if user and user.is_authenticated:
                if user.is_staff:
                    return Project.objects.select_related("owner").all()
                return Project.objects.filter(owner=user)
            return Project.objects.none()
        # Read — staff see all, public sees non-archived
        if user and user.is_authenticated and user.is_staff:
            return Project.objects.select_related("owner").all()
        return _public_queryset()

    def partial_update(self, request, *args, **kwargs):
        instance   = self.get_object()
        serializer = ProjectWriteSerializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance.refresh_from_db()
        return Response(
            ProjectSerializer(instance, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"detail": "Project deleted successfully."},
            status=status.HTTP_200_OK,
        )
