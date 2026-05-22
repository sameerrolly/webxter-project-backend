"""
URL patterns for the projects app.
Mounted at: /api/v1/projects/
"""

from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView

app_name = "projects"

urlpatterns = [
    path("", ProjectListCreateView.as_view(), name="project_list_create"),
    path("<int:pk>/", ProjectDetailView.as_view(), name="project_detail"),
]
