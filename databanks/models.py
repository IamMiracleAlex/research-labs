from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.urls import reverse

from cloudinary.models import CloudinaryField


class DataBank(models.Model):
    DRAFT, PUBLISHED = 'Draft', 'Published'
    STATUS_CHOICES = (
        (DRAFT, DRAFT),
        (PUBLISHED, PUBLISHED),
    )

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, blank=True, null=True)
    author = models.ForeignKey(
        'users.User',
        null=True,
        on_delete=models.SET_NULL
    )
    body = models.TextField(blank=True, default="")
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=DRAFT
    )
    image = CloudinaryField('image', null=True, blank=True)
    views = models.BigIntegerField(default=0)
    is_premium = models.BooleanField(default=False)
    summary = models.TextField(blank=True, default="")

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def publish(self):
        self.published_at = timezone.now()
        self.status = self.PUBLISHED
        self.save()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("databank_detail", kwargs={"pk": self.pk})
