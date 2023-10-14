from django.urls import path
from . import views


urlpatterns = [
    path('', views.PostListView.as_view(), name="post-list"),
    path(
        'category/',
        views.PostCategoryListView.as_view(),
        name="category-list"
    ),
    path(
        'themes/',
        views.ThemesView.as_view(),
        name="theme-list"
    ),
    path(
        'content-editor/',
        views.ContentEditorView.as_view(),
        name="content_editor"
    ),
    path(
        'content-editor/<int:id>/',
        views.ContentUpdateView.as_view(),
        name="content_update"
    ),
    path(
        'all-researches',
        views.AllResearchView.as_view(),
        name="all_researches"
    ),
    path('<slug:slug>', views.SinglePostView.as_view(), name="post-detail"),
    path('sectors/', views.SectorListView.as_view(), name="sector_list"),
    path('delete/', views.BulkDeletePostsView.as_view(), name="delete-posts"),
    path('bulk-action/', views.BulkActionView.as_view(), name="bulk-action"),
]
