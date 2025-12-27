from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Article
from django_elasticsearch_dsl.registries import registry

@receiver(post_save, sender=Article)
def update_article_index_and_clear_cache(sender, instance, **kwargs):
    # Update ES index
    registry.update(instance)

    # Clear recommendation cache
    cache_key = f"recommendations_{instance.id}"
    cache.delete(cache_key)

@receiver(post_delete, sender=Article)
def delete_article_index(sender, instance, **kwargs):
    registry.delete(instance)

    # Also clear recommendation cache when article is deleted
    cache_key = f"recommendations_{instance.id}"
    cache.delete(cache_key)
