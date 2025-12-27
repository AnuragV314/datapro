from django.db import models
from users.models import User
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from taggit.managers import TaggableManager
from django.urls import reverse


# Category
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("articles:article_detail", kwargs={"slug": self.slug})

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
        ]


# Article
class Article(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    tags = TaggableManager(blank=True)
    featured_image = models.ImageField(upload_to="images/articles/  ", blank=True)
    view_count = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("articles:article_detail", kwargs={"slug": self.slug})

    class Meta:
        indexes = [
            models.Index(fields=["slug", "published"]),
            models.Index(fields=["created_at"]),
        ]


# Comment

# Oct 17
# class Comment(models.Model):
#     article = models.ForeignKey(
#         Article, on_delete=models.CASCADE, related_name="comments"
#     )
#     author = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     approved = models.BooleanField(default=True)
#     parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')


#     def __str__(self):
#         return f"Comment by {self.author} on {self.article}"


class Comment(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    def __str__(self):
        return f"Comment by {self.author} on {self.article}"

    @property
    def approved_replies(self):
        return self.replies.filter(approved=True).order_by("created_at")

    @property
    def reply_count(self):
        return self.replies.filter(approved=True).count()

    class Meta:
        indexes = [
            models.Index(fields=["article", "approved"]),
            models.Index(fields=["parent"]),
        ]


# Like
class Like(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("article", "user")
        indexes = [
            models.Index(fields=["article", "user"]),
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.article.title}"


# Bookmark
class Bookmarks(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="bookmarks"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("article", "user")
        indexes = [
            models.Index(fields=["article", "user"]),
        ]

    def __str__(self):
        return f"{self.user.username} bookmarked {self.article.title}"


# Comment Report
class CommentReport(models.Model):
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="reports"
    )
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report by {self.reporter} on comment {self.comment.id}"

    class Meta:
        indexes = [
            models.Index(fields=["comment", "resolved"]),
        ]
        
        
        
        
