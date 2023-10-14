from django.contrib import admin
from django.urls import path, re_path

from users import views


app_name = 'users'

urlpatterns = [
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    path('account', views.AccountView.as_view(), name='account'),
    path(
        'plan-activate',
        views.PlanActivateView.as_view(),
        name='plan_activate'
    ),
]
