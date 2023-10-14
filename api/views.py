from rest_framework.views import APIView
from rest_framework.response import Response
from posts.models import Post
from rest_framework.permissions import IsAuthenticated
from .serializers import PostSerializer, UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your views here.
class PostView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Fetches the latest post tagged custom research and the latest post with any other tag
        """
        queryset = Post.objects.filter(status="Published")
        post1 = queryset.filter(tags__name__in=["Custom Research"]).first()
        # If no post tagged Custom Research was found, defaults to second latest post
        if post1 is None:
            post1 = queryset.exclude(tags__name__in=["Custom Research"])[1]
        post2 = queryset.exclude(tags__name__in=["Custom Research"]).first()
        posts = [post1, post2]
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class TokenVerify(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserVerify(APIView):
    """
        checks if a user exists
    """

    def post(self, request):

        email = request.data['email']

        try:
            user = User.objects.get(email =email)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"detail": "user does not exist"}, 404)
