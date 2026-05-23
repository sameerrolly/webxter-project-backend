"""
Project model — full product listing for the store.
"""

from django.conf import settings
from django.db import models


class Project(models.Model):

    class Status(models.TextChoices):
        DRAFT    = "draft",    "Draft"
        ACTIVE   = "active",   "Active"
        COMPLETED = "completed", "Completed"
        ARCHIVED = "archived", "Archived"

    class Category(models.TextChoices):
        WEB          = "web",          "Web Development"
        MOBILE       = "mobile",       "Mobile"
        DATA_SCIENCE = "data_science", "Data Science"
        AI_ML        = "ai_ml",        "AI/ML"
        DESKTOP      = "desktop",      "Desktop"
        IOT          = "iot",          "IoT"
        OTHER        = "other",        "Other"

    class Level(models.TextChoices):
        BEGINNER     = "beginner",     "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED     = "advanced",     "Advanced"
        EXPERT       = "expert",       "Expert"

    class Badge(models.TextChoices):
        NONE    = "",       "None"
        POPULAR = "popular", "Popular"
        HOT     = "hot",    "Hot"
        NEW     = "new",    "New"

    # -------------------------------------------------------------------------
    # Ownership & visibility
    # -------------------------------------------------------------------------
    owner  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    is_sold_out = models.BooleanField(default=False)

    # -------------------------------------------------------------------------
    # Basic information
    # -------------------------------------------------------------------------
    title             = models.CharField(max_length=255)
    category          = models.CharField(
        max_length=20, choices=Category.choices, default=Category.WEB, blank=True
    )
    level             = models.CharField(
        max_length=20, choices=Level.choices, default=Level.BEGINNER, blank=True
    )
    delivery_time     = models.CharField(
        max_length=100, blank=True,
        help_text="e.g. '3 days', 'Instant download'"
    )
    badge             = models.CharField(
        max_length=10, choices=Badge.choices, default=Badge.NONE, blank=True
    )
    short_description = models.CharField(max_length=500, blank=True)
    description       = models.TextField(blank=True)   # long description

    # -------------------------------------------------------------------------
    # Pricing
    # -------------------------------------------------------------------------
    sale_price     = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Selling price (₹)"
    )
    original_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Original / crossed-out price (₹)"
    )
    # Keep legacy price field for backwards compatibility
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # -------------------------------------------------------------------------
    # Tech stack & features  (stored as JSON arrays)
    # -------------------------------------------------------------------------
    technologies  = models.JSONField(
        default=list, blank=True,
        help_text="List of technology/tag strings"
    )
    key_features  = models.JSONField(
        default=list, blank=True,
        help_text="List of key feature strings"
    )
    whats_included = models.JSONField(
        default=list, blank=True,
        help_text="List of 'what's included' strings"
    )

    # -------------------------------------------------------------------------
    # Media
    # -------------------------------------------------------------------------
    thumbnail     = models.ImageField(
        upload_to="projects/thumbnails/", null=True, blank=True
    )
    demo_video_url = models.URLField(
        max_length=500, blank=True,
        help_text="YouTube URL or direct .mp4 link"
    )

    # -------------------------------------------------------------------------
    # Project links  (stored as JSON array of {type, url, label?})
    # e.g. [{"type": "github", "url": "https://..."}, ...]
    # -------------------------------------------------------------------------
    project_links = models.JSONField(
        default=list, blank=True,
        help_text="List of {type, url} dicts"
    )

    # -------------------------------------------------------------------------
    # Timestamps
    # -------------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.title


class ProjectMedia(models.Model):
    """
    Media gallery items for a project.
    Supports images and videos. Order is controlled by `order` field.
    The item with the lowest order (or is_featured=True) is the featured media.
    """

    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"
        URL   = "url",   "URL"

    project    = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="media"
    )
    media_type = models.CharField(
        max_length=10, choices=MediaType.choices, default=MediaType.IMAGE
    )
    file       = models.FileField(
        upload_to="projects/media/", null=True, blank=True
    )
    url        = models.URLField(max_length=500, blank=True)
    is_featured = models.BooleanField(default=False)
    order      = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]
        verbose_name = "Project Media"
        verbose_name_plural = "Project Media"

    def __str__(self):
        return f"{self.project.title} — {self.media_type} #{self.pk}"
