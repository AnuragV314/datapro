"""
URL configuration for datapro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include, re_path
from fastapi.middleware.wsgi import WSGIMiddleware
from apis.main import app as fastapi_app

from django.conf import settings
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap
from .sitemaps import ArticleSitemap, CategorySitemap, TagSitemap

from . import views
from django.views.generic import TemplateView

sitemaps = {
    'articles': ArticleSitemap,
    'categories': CategorySitemap,
    'tags': TagSitemap,
}



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # Allauth URLs
    path('profile/', include('users.urls')),
    path('analytics/', include('analytics.urls')),
    path('apis/', WSGIMiddleware(fastapi_app)),

    path('about/', TemplateView.as_view(template_name="pages/about.html"), name='about'),
    path('terms/', TemplateView.as_view(template_name="pages/terms.html"), name='terms'),
    path('privacy/', TemplateView.as_view(template_name="pages/privacy.html"), name='privacy'),
    path('cookies/', TemplateView.as_view(template_name="pages/cookie.html"), name='cookies'),
    path('community-guidelines/', TemplateView.as_view(template_name="pages/community_guidelines.html"), name='community_guidelines'),
    path('contact/', TemplateView.as_view(template_name="pages/contact.html"), name='contact'),

    
    
    
    path('', include('articles.urls', namespace='articles')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    # path('summernote/', include('django_summernote.urls')), # summernote URLs
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)