import os
import csv
import time
import sys
import pytz
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from events.models import Event

BASE_ENDPOINT = "https://coresight.com/wp-json/wp/v2"


class Command(BaseCommand):
    help = "Migrate events from a wordpress export"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Starting upload for event presentation...")
        )
        # Process event presentation data upload
        import_presentation_type(self)
        self.stdout.write(
            self.style.SUCCESS("Completed event presentation upload...")
        )

        # sleep for 3 secs before next process
        time.sleep(3)
        self.stdout.write(
            self.style.SUCCESS("Starting upload for event video...")
        )
        import_video_type(self)
        self.stdout.write(
            self.style.SUCCESS("Completed event video upload...")
        )


def import_presentation_type(self):
    with open('events.csv', 'r', encoding='utf-8-sig') as f:
        csv.field_size_limit(sys.maxsize)
        reader = csv.DictReader(f)
        User = get_user_model()
        counter = 0
        limit = 100 if os.environ.get("ENVIRONMENT") == "Prod" else 500

        for row in reader:
            counter += 1
            try:
                author = User.objects.first()
            except User.DoesNotExist:
                author = None
            dt = [int(x) for x in row["Date"].split("/")]
            event_date = None
            csr_dt = row['csr_event_start_date']
            if csr_dt:
                _year, _month, _day = csr_dt[:4], csr_dt[4:6], csr_dt[6:]
                event_date = datetime(
                    int(_year), int(_month), int(_day), tzinfo=pytz.UTC
                )
            else:
                event_date = datetime(
                    dt[2], dt[1], dt[0], tzinfo=pytz.UTC
                )
            image = row['Image URL'].split('|')[0]
            full_image_path = None
            if image[-3:] == 'png':
                full_image_path = f"{image}.png"
            else:
                full_image_path = f"{image}.jpg"
            event = Event(
                title=row['Title'],
                status="Published",
                excerpt=row['Excerpt'],
                author=author,
                article=row['Content'],
                banner_image=full_image_path,
                video="",
                event_type=Event.PRESENTATION,
                event_date=event_date
            )

            event.save()
            event.created_at = datetime(
                dt[2], dt[1], dt[0], tzinfo=pytz.UTC
            )

            event.save()
            self.stdout.write(
                self.style.SUCCESS(
                    (
                        "Successfully created presentation event "
                        f"with wp_id: {row['ID']}"
                    )
                )
            )
            if counter == limit:
                break
        self.stdout.write(
            self.style.SUCCESS("Upload completed...")
        )


def import_video_type(self):
    with open('videos.csv', 'r', encoding='utf-8-sig') as f:
        csv.field_size_limit(sys.maxsize)
        reader = csv.DictReader(f)
        User = get_user_model()
        counter = 0
        limit = 100 if os.environ.get("ENVIRONMENT") == "Prod" else 500

        for row in reader:
            counter += 1
            try:
                author = User.objects.first()
            except User.DoesNotExist:
                author = None
            dt = [int(x) for x in row["Date"].split("/")]
            event_date = None
            csr_dt = row['csr_date']
            if csr_dt:
                _year, _month, _day = csr_dt[:4], csr_dt[4:6], csr_dt[6:]
                event_date = datetime(
                    int(_year), int(_month), int(_day), tzinfo=pytz.UTC
                )
            else:
                event_date = datetime(
                    dt[2], dt[1], dt[0], tzinfo=pytz.UTC
                )
            image = row['Image URL'].split('|')[0]
            full_image_path = None
            if image[-3:] == 'png':
                full_image_path = f"{image}.png"
            else:
                full_image_path = f"{image}.jpg"
            event = Event(
                title=row['Title'],
                status="Published" if row['Status'] == 'publish' else "Draft",
                author=author,
                article=row['Content'],
                event_type=Event.VIDEO,
                banner_image=full_image_path,
                excerpt=row['Excerpt'],
                video=f"{row['csr_video']}.mp4",
                event_date=event_date
            )

            event.save()
            event.created_at = datetime(
                dt[2], dt[1], dt[0], tzinfo=pytz.UTC
            )

            event.save()
            self.stdout.write(
                self.style.SUCCESS(
                    (
                        "Successfully created video event "
                        f"with wp_id: {row['ID']}"
                    )
                )
            )
            if counter == limit:
                break
        self.stdout.write(
            self.style.SUCCESS("Upload completed...")
        )
