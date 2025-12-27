from django.urls import path
from . import views

app_name = "articles"

# urlpatterns = [
#     path('', views.articles, name='articles'),
# ]

urlpatterns = [
    path("", views.article_list, name="article_list"),
    path("create/", views.article_create, name="article_create"),
    path("test-redis/", views.test_redis, name="test_redis"),
    path("test-celery/", views.test_celery, name="test_celery"),
    path("search/", views.search, name="search"),
    path("<slug:slug>/", views.article_detail, name="article_detail"),
    path("<slug:slug>/comment/", views.add_comment, name="add_comment"),
    path("<slug:slug>/like/", views.toggle_like, name="toggle_like"),
    path("<slug:slug>/bookmark/", views.toggle_bookmark, name="toggle_bookmark"),
    path("<slug:slug>/edit/", views.article_edit, name="article_edit"),
    path("<slug:slug>/delete/", views.article_delete, name="article_delete"),
    path(
        "comment/<int:comment_id>/report/", views.report_comment, name="report_comment"
    ),
    path(
        "<slug:slug>/comment/<int:comment_id>/reply/", views.add_reply, name="add_reply"
    ),
]
