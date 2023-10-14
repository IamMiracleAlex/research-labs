from django.core.management.base import BaseCommand

from events.models import Event


class Command(BaseCommand):
    help = "Delete all or specific events from database"

    def handle(self, *args, **options):
        """Delete Events"""
        self.stdout.write(
            self.style.SUCCESS("Process started...")
        )
        try:
            Event.objects.all().delete()
        except Event.DoesNotExist:
            pass
        self.stdout.write(
            self.style.SUCCESS("Process completed...")
        )
