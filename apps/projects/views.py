"""
Project CRUD — users can only access their own projects.
This is also an example of a fully protected API endpoint.
"""

from rest_framework import generics, permissions
from .models import Project
from .serializers import ProjectSerializer


class ProjectListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/projects/        — list authenticated user's projects
    POST /api/v1/projects/        — create a new project
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users only see their own projects
        return Project.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/projects/<id>/  — retrieve a project
    PATCH  /api/v1/projects/<id>/  — partial update
    DELETE /api/v1/projects/<id>/  — delete
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)
