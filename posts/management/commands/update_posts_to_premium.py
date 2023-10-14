import random
from django.core.management.base import BaseCommand
from posts.models import Post


class Command(BaseCommand):
    help = 'Update random posts to premium for test purposes'

    def handle(self, *args, **kwargs):
        posts = Post.objects.filter(is_premium=False)
        for _ in range(20):
            post = posts[random.randint(0, len(posts)-1)]
            post.is_premium = True
            post.save()
