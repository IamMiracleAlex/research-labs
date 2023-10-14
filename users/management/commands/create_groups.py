from django.core.management.base import BaseCommand
from users.utils import create_groups_with_permissions


class Command(BaseCommand):
    help = 'Create groups and assign permissions'

    def handle(self, *args, **kwargs):
        create_groups_with_permissions()
