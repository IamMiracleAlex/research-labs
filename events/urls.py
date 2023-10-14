from django.urls import path

from events import views


urlpatterns = [
    path('', views.EventListView.as_view(), name="event_list"),
    path('<int:pk>/', views.EventDetailView.as_view(), name="event_detail"),
    path('create/', views.EventCreateView.as_view(), name="event_create"),
    path('admin-list/', views.EventAdminView.as_view(), name="event_admin")
]
