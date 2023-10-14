from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('latest/', views.PostView.as_view()),
    path('user-verify/', views.UserVerify.as_view()),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api-token-verify/', views.TokenVerify.as_view(), name="api_token_verify")
]
