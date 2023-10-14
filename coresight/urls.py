"""coresight URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap

from users import views as user_views
from posts.views import IndexPostView

from coresight.sitemaps import coresight_sitemap


urlpatterns = [
    path('', IndexPostView.as_view(), name="index"),
    path('core/', admin.site.urls),
    path('users/', include('users.urls'), name='users'),
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),

    path('research/', include('posts.urls'), name="posts"),
    path('api/', include('api.urls'), name="api"),
    path('cookies/', include('cookie_consent.urls')),
    path('events/', include('events.urls')),
    path('databanks/', include('databanks.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': coresight_sitemap}, name='django.contrib.sitemaps.views.sitemap'),
]
# authentication urls
urlpatterns += [
    path(
        'login/',
        user_views.LoginView.as_view(),
        name='auth-login'
    ),
    path('signup/', user_views.RegistrationView.as_view(), name='signup'),
    path('auth/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('auth/password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('auth/password_reset/done/', auth_views.PasswordResetDoneView .as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    re_path(r'auth/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('auth/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path(
        'auth/logout/',
        auth_views.LogoutView.as_view(),
        name='logout',
    ),
    path(
        'premium-request',
        user_views.PremiumRequestView.as_view(),
        name='premium_request'
    )
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
