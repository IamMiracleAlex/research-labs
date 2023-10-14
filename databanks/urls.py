from django.urls import path

from databanks import views


urlpatterns = [
    path('', views.DataBankListView.as_view(), name="databank_list"),
    path('<int:pk>/', views.DataBankDetailView.as_view(), name="databank_detail"),
]