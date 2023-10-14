import os
import csv
import sys
import string
import requests
import pytz
from datetime import datetime
import random
from tempfile import NamedTemporaryFile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from posts.models import (
    PostBody,
    Sector,
    Theme,
    Post
)
BASE_ENDPOINT = "https://coresight.com/wp-json/wp/v2"


class Command(BaseCommand):
    help = "Migrate posts from a wordpress export"

    def handle(self, *args, **options):
        with open('Blog-Posts.csv', 'r', encoding='utf-8-sig') as f:
            csv.field_size_limit(sys.maxsize)
            reader = csv.DictReader(f)
            User = get_user_model()
            counter = 0
            limit = 100 if os.environ.get("ENVIRONMENT") == "Prod" else 5000

            for row in reader:
                counter += 1
                try:
                    author = User.objects.get(email=row['Author Email'])
                except User.DoesNotExist:
                    author = None
                dt = [int(x) for x in row["Date"].split("-")]
                post = Post(
                    title=row['Title'],
                    status=(
                        "Draft" if row['Status'] == "draft"
                        else "Published"
                    ),
                    author=author,
                    excerpt=row['Excerpt'],
                    published_at=datetime(dt[0], dt[1], dt[2], tzinfo=pytz.UTC)
                )

                post.save()
                if row["Research Themes"]:
                    themes = row["Research Themes"].split('|')
                    for theme in themes:
                        theme, _ = Theme.objects.get_or_create(name=theme)
                        post.themes.add(theme)

                if row["Retail Sector Coverage"]:
                    sectors = row["Retail Sector Coverage"].split('|')[0]
                    for sector in sectors:
                        sector, _ = Sector.objects.get_or_create(name=sector)
                        post.sectors.add(sector)

                
                post.tags.add(*self.build_tags(row))
                post.created_at = datetime(
                    dt[0], dt[1], dt[2], tzinfo=pytz.UTC
                )
                post.save()
                PostBody.objects.create(
                    title="Full Article",
                    text=row['Content'],
                    post=post
                )

                if row["Image URL"]:
                    self.get_remote_image(post, row)
                    self.stdout.write(
                        self.style.SUCCESS(
                            (
                                "Successfully created post "
                                f"with wp_id: {row['ID']}"
                            )
                        )
                    )

                if counter == limit:
                    break

    def build_tags(self, row):
        tags = []
        tags.extend(row['Categories'].split('|'))
        tags.extend(row['Tags'].split('|'))
        tags.extend(row['Research Products'].split('>'))
        tags = [tag.strip() for tag in tags]

        return tags

    def get_remote_image(self, post, row):
        post_url = f"{BASE_ENDPOINT}/posts/{row['ID']}"
        try:
            post_response = requests.get(post_url).json()

            # extract the image id and make another request
            image_id = post_response.get("featured_media")
            if image_id:
                # construct the image endpoint and make the request
                _image_url = f"{BASE_ENDPOINT}/media/{image_id}"
                image_response = requests.get(_image_url).json()
                image_url = (
                    image_response
                    .get("media_details")
                    .get("sizes")
                    .get("full")
                    .get("source_url")
                )
                if image_url:
                    post.image = f"{image_url}.jpg"
                    post.save()
        except Exception:
            self.stdout.write(
                self.style.ERROR("No image url for this post")
            )
