# from django.contrib.sitemaps import Sitemap
# from articles.models import Article

# class ArticleSitemap(Sitemap):
#     changefreq = "daily"
#     priority = 0.5

#     def items(self):
#         return Article.objects.filter(published=True)

#     def lastmod(self, obj):
#         return obj.updated_at




# articles/sitemaps.py
from django.contrib.sitemaps import Sitemap
from articles.models import Article, Category
from taggit.models import Tag  # if you're using django-taggit


class ArticleSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Article.objects.filter(published=True).order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Category.objects.all().order_by('name')

    def location(self, obj):
        return obj.get_absolute_url()


class TagSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.4

    def items(self):
        return Tag.objects.all().order_by('name')

    def location(self, obj):
        return f"/tag/{obj.slug}/"
