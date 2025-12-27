from allauth.account.signals import user_logged_in
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import User
from articles.models import Article

# @receiver(user_logged_in)
# def update_google_profile_picture(request, user, **kwargs):
#     social_account = user.socialaccount_set.filter(provider='google').first()
#     if social_account:
#         picture_url = social_account.extra_data.get('picture')
#         if picture_url and user.profile_image != picture_url:
#             user.profile_image = picture_url
#             user.save()

# @receiver([post_save, post_delete], sender=Article)
# def update_expert_status(sender, instance, **kwargs):
#     """Automatically check and update author's expert status."""
#     if instance.author:
#         instance.author.check_expert_status()

import logging
from allauth.account.signals import user_logged_in
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import User
from articles.models import Article

# Set up logger for this file
logger = logging.getLogger(__name__)


# Update Google profile picture when user logs in
@receiver(user_logged_in)
def update_google_profile_picture(request, user, **kwargs):
    social_account = user.socialaccount_set.filter(provider='google').first()
    if social_account:
        picture_url = social_account.extra_data.get('picture')
        if picture_url and user.profile_image != picture_url:
            user.profile_image = picture_url
            user.save()
            logger.info(f"Updated Google profile picture for user: {user.username}")
        else:
            logger.info(f"ℹNo new profile picture found for user: {user.username}")
    else:
        logger.info(f"No Google social account found for user: {user.username}")


# Update expert status automatically on article save or delete
@receiver([post_save, post_delete], sender=Article)
def update_expert_status(sender, instance, **kwargs):
    """Automatically check and update author's expert status."""
    if instance.author:
        old_status = instance.author.is_expert
        instance.author.check_expert_status()
        new_status = instance.author.is_expert

        if old_status != new_status:
            if new_status:
                logger.info(f"{instance.author.username} has become an expert (5+ published articles).")
            else:
                logger.info(f"{instance.author.username} is no longer an expert (less than 5 published).")
        else:
            logger.debug(f"Expert status unchanged for {instance.author.username}.")
