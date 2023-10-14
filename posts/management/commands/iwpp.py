import csv
import sys
import requests
import pytz
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from posts.models import (
    PostBody,
    Sector,
    Theme,
    Post,
    Product,
    Region,
    Company,
)
BASE_ENDPOINT = "https://coresight.com/wp-json/wp/v2"


class Command(BaseCommand):
    help = "Migrate posts from a wordpress export"

    def handle(self, *args, **options):
        with open('Blog-Posts-Export-2022.csv', 'r', encoding='utf-8-sig') as f:
            csv.field_size_limit(sys.maxsize)
            reader = csv.DictReader(f)
            User = get_user_model()
            counter = 0
            limit = 100 

            for row in reader:
                counter += 1
                print(f"{counter} - {row['Title']}")
                try:
                    author = User.objects.get(email=row['Author Email'])
                except User.DoesNotExist:
                    author = None
                dt = datetime.fromtimestamp(int(row["Date"]), tz=pytz.timezone('America/New_York'))
                post = Post(
                    title=row['Title'],
                    status=(
                        "Draft" if row['Status'] == "draft"
                        else "Published"
                    ),
                    author=author,
                    excerpt=row['Excerpt'],
                    published_at=dt
                )

                post.save()
                if row["Research Themes"]:
                    themes = row["Research Themes"].split('|')
                    for theme in themes:
                        theme, created = Theme.objects.get_or_create(name=theme)
                        post.themes.add(theme)

                if row["Retail Sector Coverage"]:
                    sectors = row["Retail Sector Coverage"].split('|')
                    for sector in sectors:
                        sector, created = Sector.objects.get_or_create(name=sector)
                        post.sectors.add(sector)

                if row["Research Products"]:
                    products = row["Research Products"].split('>')
                    for product in products:
                        product, created = Product.objects.get_or_create(name=product)
                        post.products.add(product)

                if row["Region"]:
                    regions = row["Region"].split('|')
                    for region in regions:
                        region, created = Region.objects.get_or_create(name=region)
                        post.regions.add(region)

                if row["primary_company_name"]:
                    companies = row["primary_company_name"].split('|')
                    for company in companies:
                        company, created = Company.objects.get_or_create(name=company)
                        post.companies.add(company)

                
                post.tags.add(*self.build_tags(row))
                post.created_at = dt
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
