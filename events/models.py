from cloudinary.models import CloudinaryField
from django.db import models
from taggit.managers import TaggableManager

import readtime


class Event(models.Model):
    DRAFT, PUBLISHED = 'Draft', 'Published'
    STATUS_CHOICES = (
        (DRAFT, DRAFT),
        (PUBLISHED, PUBLISHED),
    )
    VIDEO, PRESENTATION = "video", "presentation"
    EVENT_TYPE = (
        (VIDEO, VIDEO),
        (PRESENTATION, PRESENTATION),
    )

    title = models.CharField(max_length=250)
    banner_image = CloudinaryField(blank=True, null=True)
    event_date = models.DateField()
    video = CloudinaryField(
        resource_type="video",
        blank=True,
        null=True
    )
    event_type = models.CharField(
        max_length=15,
        choices=EVENT_TYPE,
        blank=True,
    )
    excerpt = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=DRAFT
    )
    tags = TaggableManager(blank=True)
    author = models.ForeignKey(
        'users.User',
        null=True,
        on_delete=models.SET_NULL
    )
    article = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def get_read_time(self):
        result = readtime.of_text(self.article)
        return result.text
