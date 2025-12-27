from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    bio = models.TextField(blank=True)
    expertise = models.CharField(max_length=255, blank=True)
    # profile_image = models.URLField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='images/profiles/', blank=True, null=True)
    is_expert = models.BooleanField(default=False)
    
    # def check_expert_status(self):
    #     from articles.models import Article
    #     if Article.objects.filter(author=self, published=True).count() >= 5:  
    #         self.is_expert = True
    #         self.save()

    def check_expert_status(self):
        from articles.models import Article
        published_count = Article.objects.filter(author=self, published=True).count()
        new_status = published_count >= 30
        if self.is_expert != new_status:
            self.is_expert = new_status
            self.save()

    
    
    
    
    
    
    
    