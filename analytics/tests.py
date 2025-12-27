from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from articles.models import Article
from .models import ArticleView
from django.urls import reverse

class AnalyticsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser', email='test@example.com', password='password'
        )
        self.admin = get_user_model().objects.create_superuser(
            username='admin', email='admin@example.com', password='password'
        )
        self.client.login(username='admin', password='password')
        self.article = Article.objects.create(
            title='Test Article', author=self.user, slug='test-article'
        )

    def test_analytics_dashboard_access(self):
        response = self.client.get(reverse('analytics_dashboard'))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, 'Analytics Dashboard')

    def test_analytics_dashboard_non_admin(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('analytics_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_article_view_tracking(self):
        ArticleView.objects.create(article=self.article, user=self.user)
        self.assertEqual(self.article.view_count.count(), 1)