# The block below must not be removed and must come first before any imports.
import os
import django
                                                              
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coresight.settings")
django.setup()
########################################################################                                                   
print("Ready..!")

import csv
from django.utils import timezone
from posts.models import Post
from users.models import User

path = 'exported_data.csv'
author = User.objects.first()

with open(path, "r") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        Post.objects.create(author=author, title=row[0], body=row[1],
                            excerpt="As part of our Head-to-Head series, we compare Aldi and Lidl, "
                                        "two major players in discount grocery retail.",
                            status=Post.PUBLISHED, published_at=timezone.now())
      
print("Posts created successfully..!")
# posts.append(Post(user=user, title=row[0], body=row[1]))
# Post.objects.bulk_create(posts)