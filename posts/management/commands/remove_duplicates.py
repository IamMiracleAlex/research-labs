from django.core.management.base import BaseCommand

from posts.models import (
    Post
)

class Command(BaseCommand):
    help = "Remove duplicate posts"

    def handle(self, *args, **options):
        for post in Post.objects.all():
            if Post.objects.filter(title=post.title).count() > 1:
                post.delete()