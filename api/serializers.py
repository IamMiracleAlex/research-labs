from rest_framework import serializers
from posts.models import Post
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)
from django.contrib.auth import get_user_model

User = get_user_model()


class PostSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ("title", "slug", "excerpt", "author", "image", "tags")

    def get_image(self, obj):
        if obj.image:
            return obj.image.url


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")
