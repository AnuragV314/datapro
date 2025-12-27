# articles/tests.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Article, Comment, Like
from django.urls import reverse
from channels.testing import WebsocketCommunicator
from datapro.asgi import application
from asgiref.sync import sync_to_async
import json

class ArticleTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser', email='test@example.com', password='password'
        )
        self.author = get_user_model().objects.create_user(
            username='author', email='author@example.com', password='password'
        )
        self.client.login(username='testuser', password='password')
        self.article = Article.objects.create(
            title='Test Article', author=self.author, slug='test-article'
        )

    def test_article_creation(self):
        self.assertEqual(self.article.title, 'Test Article')

    def test_article_list_view(self):
        response = self.client.get(reverse('articles:article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Article')

    def test_comment_creation(self):
        Comment.objects.create(article=self.article, author=self.user, content='Test comment')
        self.assertEqual(self.article.comments.count(), 1)

    def test_like_toggle(self):
        response = self.client.post(
            reverse('articles:toggle_like', args=[self.article.slug]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.article.likes.count(), 1)
        response = self.client.post(
            reverse('articles:toggle_like', args=[self.article.slug]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(self.article.likes.count(), 0)

    # async def test_notification(self):
    #     communicator = WebsocketCommunicator(application, "/ws/notifications/")
    #     communicator.scope['user'] = self.author
    #     connected, _ = await communicator.connect()
    #     self.assertTrue(connected)
    #     # Run database operation outside test transaction
    #     def create_like():
    #         return Like.objects.create(article=self.article, user=self.user)

    #     await sync_to_async(create_like)()

    #     # Send notification
    #     await communicator.send_json_to({
    #         'type': 'send_notification',
    #         'message': f'{self.user.username} liked your article "{self.article.title}"'
    #     })
    #     response = await communicator.receive_json_from()
    #     self.assertEqual(response['message'], f'{self.user.username} liked your article "{self.article.title}"')
    #     await communicator.disconnect()
    
    
    def test_category_filter(self):
        response = self.client.get(reverse('article_list') + '?category=machine-learning')
        self.assertContains(response, 'Test Article')

    def test_tag_filter(self):
        response = self.client.get(reverse('article_list') + '?tag=data-science')
        self.assertContains(response, 'Test Article')

    def test_user_profile(self):
        response = self.client.get(reverse('user_profile', args=[self.author.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Article')
    
    
    
    
    