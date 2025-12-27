from celery import shared_task
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_notification_email(user_email, article_title):
    try:
        logger.info(f"Sending notification to {user_email} for article {article_title}")
        send_mail(
            'New Article Published',
            f'Your new article "{article_title}" has been published!',
            'vermagup01@gmail.com',
            [user_email],
            fail_silently=False,
        )
        logger.info("Email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")



