from django.contrib import admin
from .models import Article, Bookmarks, Comment, Like, Category, CommentReport
from taggit.models import Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "created_at", "category"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["article", "author", "created_at", "approved"]
    actions = ["approve_comments"]

    def approve_comments(self, request, queryset):
        queryset.update(approved=True)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ["article", "user", "created_at"]


@admin.register(Bookmarks)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ["article", "user", "created_at"]
    

@admin.register(CommentReport)
class CommentReportAdmin(admin.ModelAdmin):
    list_display = ['comment', 'reporter', 'created_at', 'resolved']
    actions = ['resolve_reports']

    def resolve_reports(self, request, queryset):
        queryset.update(resolved=True)
