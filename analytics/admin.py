from django.contrib import admin
from .models import ArticleView

@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    list_display = ['article', 'user', 'view_date']
    list_filter = ['view_date']