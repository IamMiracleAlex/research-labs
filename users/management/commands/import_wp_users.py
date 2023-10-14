import csv
import sys
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import get_hasher
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Migrate users from a wordpress export"

    def handle(self, *args, **options):
        with open('user-export.csv', 'r', encoding='utf-8-sig') as f:
            csv.field_size_limit(sys.maxsize)  # Increment the field size limit
            reader = csv.DictReader(f)
            User = get_user_model()
            hasher = get_hasher('phpass')
            chunk = []

            for row in reader:
                # Importing only users with coresight email
                # Remove this block to import all users
                if 'coresight' not in row['user_email']:
                    continue

                if not User.objects.filter(email=row['user_email']).exists():
                    user = User(
                        email=row['user_email'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        company_name=row['mepr_company'],
                        password=hasher.from_orig(row['user_pass']),
                        is_staff=True,
                        is_superuser=True

                    )
                    chunk.append(user)

                    if len(chunk) == 100:
                        User.objects.bulk_create(chunk)
                        chunk = []

            User.objects.bulk_create(chunk)
