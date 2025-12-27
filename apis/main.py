import os
import django
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datapro.settings')
django.setup()

# Now import Django models
from django.contrib.auth.models import User
from articles.models import Article, Like, Comment
from analytics.models import ArticleView

app = FastAPI()

class ArticleResponse(BaseModel):
    id: int
    title: str
    slug: str
    like_count: int


@app.get("/test/")
def test_endpoint():
    return {"message": "FastAPI is working"}


@app.get("/articles/", response_model=List[ArticleResponse])
def get_articles():
    try:
        articles = Article.objects.all()
        return [
            ArticleResponse(
                id=article.id,
                title=article.title,
                slug=article.slug,
                like_count=article.likes.count()
            ) for article in articles
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching articles: {str(e)}")


@app.get("/analytics/summary/")
def get_analytics_summary():
    return {
        "total_articles": Article.objects.all().count(),
        "total_views": ArticleView.objects.all().count(),
        "total_likes": Like.objects.all().count(),
        "total_comments": Comment.objects.all().count(),

    }