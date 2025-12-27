from django.db import models
from articles.models import Article
from users.models import User

class ArticleView(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    view_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} viewed {self.article} on {self.view_date}"




    