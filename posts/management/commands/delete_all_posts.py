from django.core.management.base import BaseCommand

from posts.models import Post


class Command(BaseCommand):
    help = "Delete all or specific posts from database"

    def add_arguments(self, parser):
        parser.add_argument('post_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        """Delete posts"""
        self.stdout.write(
            self.style.SUCCESS("Process started...")
        )
        try:
            Post.objects.all().delete()
        except Post.DoesNotExist:
            pass
        self.stdout.write(
            self.style.SUCCESS("Process completed...")
        )
