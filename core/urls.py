"""
Root URL configuration.
All app routes are namespaced under /api/v1/.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/auth/", include("apps.accounts.urls", namespace="accounts")),
    path("api/v1/projects/", include("apps.projects.urls", namespace="projects")),
    path("api/v1/orders/", include("apps.orders.urls", namespace="orders")),
]

# Serve media files in both development and production.
# In production, a proper web server (nginx/caddy) should handle /media/ instead,
# but this fallback ensures avatars are always accessible during development.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files in development only (whitenoise handles production)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
