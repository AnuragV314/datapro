from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from analytics.models import ArticleView
from users.models import User
from .models import Article, Bookmarks, Category, Like, Comment, CommentReport
from .forms import ArticleForm, CommentForm
from pymongo import MongoClient
from slugify import slugify
from django.http import JsonResponse
from .tasks import send_notification_email
from celery.exceptions import OperationalError as CeleryOperationalError
from django.db.models import Q
import logging

from redis import Redis
from django.http import HttpResponse

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django_elasticsearch_dsl.search import Search
from django.views.decorators.cache import cache_page
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache

from django.utils import timezone

import re
from collections import Counter
from django.core.paginator import Paginator

logger = logging.getLogger(__name__)


client = MongoClient(
    "mongodb+srv://anuragpy:s6w1Zfl4DqVlrLqy@datapro.2nkidq5.mongodb.net/?retryWrites=true&w=majority&appName=datapro"
)
db = client["datapro_content"]
articles_collection = db["articles"]
articles_collection.create_index([("article_id", 1)])
articles_collection.create_index([("slug", 1)])


def test_redis(request):
    try:
        r = Redis(host="localhost", port=6379, db=0)
        r.ping()
        return HttpResponse("Redis connection successful")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return HttpResponse(f"Redis connection failed: {e}")


def test_celery(request):
    try:
        r = Redis(host="127.0.0.1", port=6379, db=0)
        r.ping()
        logger.info("Redis connection successful")
        send_notification_email.delay("vermagup01@gmail.com", "Test from Web")
        logger.info("Celery task queued successfully")
        return HttpResponse("Celery task queued successfully")
    except CeleryOperationalError as e:
        logger.error(f"Celery error: {e}")
        return HttpResponse(f"Celery error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return HttpResponse(f"Unexpected error: {e}")


# Comment Report
# oct 11
# def is_spam(content):
#     """Simple spam filter: flags if more than 3 URLs present."""
#     url_pattern = re.compile(r'http[s]?://')
#     return len(url_pattern.findall(content)) > 3


def is_spam(content):
    """
    Enhanced spam detection:
    - Too many URLs (3+)
    - Repeated words (spammy repetition)
    - Banned keywords (ads, adult, etc.)
    - Excessive length (copy-paste spam)
    """
    content_lower = content.lower().strip()

    # Too many URLs
    url_pattern = re.compile(r"http[s]?://")
    if len(url_pattern.findall(content_lower)) > 3:
        return True

    # Repeated words (e.g., "buy buy buy", "click click click")
    words = re.findall(r"\b\w+\b", content_lower)
    word_counts = Counter(words)
    if any(count > 5 for count in word_counts.values()):  # same word >5 times
        return True

    # Banned or spammy keywords
    banned_keywords = [
        "buy now",
        "click here",
        "free money",
        "visit my site",
        "cheap",
        "viagra",
        "earn cash",
        "subscribe",
        "adult",
        "xxx",
        "loan offer",
        "investment opportunity",
        "promotion",
        "betting",
    ]
    if any(keyword in content_lower for keyword in banned_keywords):
        return True

    # Excessive length (e.g., bot spam or pasted junk)
    if len(content_lower) > 2000:
        return True

    # Too many emojis or special symbols (emoji spam)
    emoji_pattern = re.compile(
        r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]+", flags=re.UNICODE
    )
    if len(emoji_pattern.findall(content)) > 10:
        return True

    return False


# Article List

# oct 17
# @cache_page(60 * 15)
# def article_list(request):
#     category_slug = request.GET.get("category")
#     tag_slug = request.GET.get("tag")
#     articles = Article.objects.filter(published=True).order_by(
#         "-created_at"
#     )  # Only published articles
#     if category_slug:
#         articles = articles.filter(category__slug=category_slug)
#     if tag_slug:
#         articles = articles.filter(tags__slug=tag_slug)
#     categories = Category.objects.all()
#     return render(
#         request, "articles/list.html", {"articles": articles, "categories": categories}
#     )


# @cache_page(60 * 15)
# def article_list(request):
#     category_slug = request.GET.get("category")
#     tag_slug = request.GET.get("tag")
#     articles = (
#         Article.objects.filter(published=True)
#         .order_by("-created_at")
#         .select_related("author", "category")
#         .prefetch_related("tags")
#     )

#     if category_slug:
#         articles = articles.filter(category__slug=category_slug)
#     if tag_slug:
#         articles = articles.filter(tags__slug=tag_slug)

#     paginator = Paginator(articles, 8)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     categories = Category.objects.all()

#     return render(
#         request,
#         "articles/list.html",
#         {
#             "page_obj": page_obj,
#             "articles": page_obj.object_list,
#             "categories": categories,
#         },
#     )


def article_list(request):
    category_slug = request.GET.get("category")
    tag_slug = request.GET.get("tag")

    cache_key = f"articles_{category_slug}_{tag_slug}"
    articles = cache.get(cache_key)

    if not articles:
        articles = (
            Article.objects.filter(published=True)
            .order_by("-created_at")
            .select_related("author", "category")
            .prefetch_related("tags")
        )
        if category_slug:
            articles = articles.filter(category__slug=category_slug)
        if tag_slug:
            articles = articles.filter(tags__slug=tag_slug)
            
        articles = list(articles)
        cache.set(cache_key, articles, 60 * 15)

    paginator = Paginator(articles, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(
        request,
        "articles/list.html",
        {
            "page_obj": page_obj,
            "articles": page_obj.object_list,
            "categories": categories,
        },
    )


# Create Article
# @login_required
# def article_create(request):
#     if request.method == "POST":
#         form = ArticleForm(request.POST, request.FILES)
#         if form.is_valid():
#             article = form.save(commit=False)
#             article.author = request.user
#             article.save()
#             # Save content to MongoDB
#             articles_collection.insert_one(
#                 {
#                     "article_id": article.id,
#                     "content": form.cleaned_data["content"],
#                     "slug": article.slug,
#                 }
#             )

#             # send notification
#             send_notification_email.delay(request.user.email, article.title)
#             return redirect("articles:article_list")
#     else:
#         form = ArticleForm()
#     return render(request, "articles/create.html", {"form": form})


@login_required
def article_create(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.published = form.cleaned_data.get("published")
            article.save()
            form.save_m2m()  # Save many-to-many relationships like tags
            articles_collection.insert_one(
                {
                    "article_id": article.id,
                    "content": form.cleaned_data["content"],
                    "slug": article.slug,
                }
            )
            # if you notify article author (current user) that his article is published
            # channel_layer = get_channel_layer()
            # async_to_sync(channel_layer.group_send)(
            #     f'user_{article.author.id}',
            #     {
            #         'type': 'send_notification',
            #         'message': f'Your article "{article.title}" was published'
            #     }
            # )
            try:
                logger.info(
                    f"Queueing notification for {request.user.email} about article {article.title}"
                )
                send_notification_email.delay(request.user.email, article.title)
                logger.info("Notification queued successfully")
            except CeleryOperationalError as e:
                logger.error(f"Celery error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
            return redirect("articles:article_list")
    else:
        form = ArticleForm()
    return render(request, "articles/create.html", {"form": form})


# @login_required
# def article_create(request):
#     if request.method == 'POST':
#         form = ArticleForm(request.POST, request.FILES)
#         if form.is_valid():
#             article = form.save(commit=False)
#             article.author = request.user
#             article.save()
#             articles_collection.insert_one({
#                 'article_id': article.id,
#                 'content': form.cleaned_data['content'],
#                 'slug': article.slug
#             })
#             try:
#                 # Test Redis connection
#                 r = Redis(host='localhost', port=6379, db=0)
#                 r.ping()
#                 logger.info("Redis connection successful in article_create")
#                 print('================================Redis connection successful================================')
#                 print(f'================================Queueing notification for {request.user.email} about article {article.title}================================')
#                 logger.info(f"Queueing notification for {request.user.email} about article {article.title}")
#                 send_notification_email.delay(request.user.email, article.title)
#                 print('================================Notification queued successfully================================')
#                 logger.info("Notification queued successfully")
#             except CeleryOperationalError as e:
#                 print(f'================================Celery error: {e}================================')
#                 logger.error(f"Celery error: {e}")
#             except Exception as e:
#                 print(f'================================Unexpected error: {e}================================')
#                 logger.error(f"Unexpected error: {e}")
#             return redirect('articles:article_list')
#     else:
#         form = ArticleForm()
#     return render(request, 'articles/create.html', {'form': form})


# Article Detail

# at oct 16
# @cache_page(60 * 15)
# def article_detail(request, slug):
#     article = get_object_or_404(Article, slug=slug)

#     if (
#         not article.published
#         and article.author != request.user
#         and not request.user.is_superuser
#     ):
#         return redirect("articles:article_list")  # Restrict drafts

#     # Create a key for tracking this article in the session
#     session_key = f"viewed_article_{article.id}"

#     # Check if this article was already viewed in this session
#     if not request.session.get(session_key, False):
#         article.view_count += 1
#         article.save()

#         # Mark as viewed
#         request.session[session_key] = True

#     # Record the view in analytics
#     ArticleView.objects.create(
#         article=article, user=request.user if request.user.is_authenticated else None
#     )

#     mongo_doc = articles_collection.find_one({"article_id": article.id})
#     content = mongo_doc["content"] if mongo_doc and "content" in mongo_doc else ""

#     approved_comments = article.comments.filter(approved=True).order_by("-created_at")
#     comment_form = CommentForm()

#     # Recommendations
#     cache_key = f"recommendations_{article.id}"
#     recommendations = cache.get(cache_key)
#     if not recommendations:
#         search = (
#             Search(index="articles")
#             .query(
#                 "bool",
#                 should=[
#                     {
#                         "match": {
#                             "category.name": (
#                                 article.category.name if article.category else ""
#                             )
#                         }
#                     },
#                     {"terms": {"tags": [tag.name for tag in article.tags.all()]}},
#                 ],
#             )
#             .exclude("term", id=article.id)[:5]
#         )
#         response = search.execute()
#         recommendations = [Article.objects.get(id=hit.meta.id) for hit in response]
#         cache.set(cache_key, recommendations, 60 * 60)  # Cache for 1 hour
#     return render(
#         request,
#         "articles/detail.html",
#         {
#             "article": article,
#             "content": content,
#             "comments": approved_comments,
#             "comment_form": comment_form,
#             'recommendations': recommendations
#         },
#     )


# @cache_page(60 * 15)
# def article_detail(request, slug):
#     article = get_object_or_404(Article, slug=slug)

#     # Restrict drafts to author or superuser only
#     if (
#         not article.published
#         and article.author != request.user
#         and not request.user.is_superuser
#     ):
#         return redirect("articles:article_list")

#     # Track unique views in the session
#     session_key = f"viewed_article_{article.id}"
#     if not request.session.get(session_key, False):
#         article.view_count += 1
#         article.save()
#         request.session[session_key] = True

#     # Record analytics (track even anonymous users)
#     ArticleView.objects.create(
#         article=article, user=request.user if request.user.is_authenticated else None
#     )

#     # Get article content from MongoDB
#     mongo_doc = articles_collection.find_one({"article_id": article.id})
#     content = mongo_doc["content"] if mongo_doc and "content" in mongo_doc else ""

#     # Comments
#     approved_comments = article.comments.filter(approved=True).order_by("-created_at")
#     comment_form = CommentForm()

#     # --- RECOMMENDATION LOGIC ---
#     cache_key = f"recommendations_{article.id}"
#     recommendations = cache.get(cache_key)

#     if not recommendations:
#         try:
#             search = Search(index="articles")

#             # If article has tags or category
#             if article.tags.exists() or article.category:
#                 should_clauses = []
#                 if article.category:
#                     should_clauses.append({
#                         "match": {
#                             "category.name": {
#                                 "query": article.category.name,
#                                 "boost": 1.0
#                             }
#                         }
#                     })
#                 if article.tags.exists():
#                     should_clauses.append({
#                         "terms": {
#                             "tags": [tag.name for tag in article.tags.all()],
#                             "boost": 2.0
#                         }
#                     })

#                 search = search.query(
#                     "bool",
#                     should=should_clauses,
#                     minimum_should_match=1
#                 ).exclude("term", id=article.id)[:5]

#             # Fallback: if no tags/category, use “more_like_this”
#             else:
#                 search = (
#                     Search(index="articles")
#                     .query(
#                         "more_like_this",
#                         fields=["title", "excerpt"],
#                         like=[{"_id": article.id}],
#                     )[:4]
#                 )

#             response = search.execute()
#             ids = [hit.meta.id for hit in response]

#             # Single optimized DB call instead of multiple .get()
#             recommendations = list(
#                 Article.objects.filter(id__in=ids, published=True)
#             )

#         except Exception as e:
#             print(f"Recommendation error: {e}")
#             # Fallback if ES fails or returns nothing
#             recommendations = list(
#                 Article.objects.filter(published=True)
#                 .exclude(id=article.id)
#                 .order_by("?")[:4]
#             )

#         # Cache for 1 hour
#         cache.set(cache_key, recommendations, 60 * 60)

#     # Render the template
#     return render(
#         request,
#         "articles/detail.html",
#         {
#             "article": article,
#             "content": content,
#             "comments": approved_comments,
#             "comment_form": comment_form,
#             "recommendations": recommendations,
#         },
#     )


# @cache_page(60 * 15)
def article_detail(request, slug):
    article = get_object_or_404(
        Article.objects.select_related("author", "category").prefetch_related(
            "tags", "comments__author", "comments__replies", "likes", "bookmarks"
        ),
        slug=slug,
    )

    # Restrict drafts
    if (
        not article.published
        and article.author != request.user
        and not request.user.is_superuser
    ):
        return redirect("articles:article_list")

    # Track unique views
    session_key = f"viewed_article_{article.id}"
    if not request.session.get(session_key, False):
        article.view_count += 1
        article.save()
        request.session[session_key] = True

    # Record analytics
    ArticleView.objects.create(
        article=article, user=request.user if request.user.is_authenticated else None
    )

    # MongoDB content
    mongo_doc = articles_collection.find_one({"article_id": article.id})
    content = mongo_doc["content"] if mongo_doc and "content" in mongo_doc else ""

    # Comments
    approved_comments = article.comments.filter(approved=True).order_by("-created_at")
    comment_form = CommentForm()

    # --- RECOMMENDATIONS ---
    cache_key = f"recommendations_{article.id}"
    recommendations = cache.get(cache_key)

    if not recommendations:
        try:
            search = Search(index="articles")
            should_clauses = []

            # Prefer articles with both category and tags
            if article.category:
                should_clauses.append(
                    {
                        "match": {
                            "category.name": {
                                "query": article.category.name,
                                "boost": 1.0,
                            }
                        }
                    }
                )
            if article.tags.exists():
                should_clauses.append(
                    {
                        "terms": {
                            "tags": [tag.name for tag in article.tags.all()],
                            "boost": 2.0,
                        }
                    }
                )

            # Only query Elasticsearch if there is at least one clause
            if should_clauses:
                search = search.query(
                    "bool", should=should_clauses, minimum_should_match=1
                ).exclude("term", id=article.id)[:5]
            else:
                # Fallback: use “more_like_this” on title/excerpt
                search = search.query(
                    "more_like_this",
                    fields=["title", "excerpt"],
                    like=[{"_id": article.id}],
                )[:5]

            response = search.execute()
            es_ids = [hit.meta.id for hit in response]

            # Fetch from DB, preserve order returned by Elasticsearch
            recommendations_qs = Article.objects.filter(
                id__in=es_ids, published=True
            ).exclude(id=article.id)
            # Preserve ES order
            recommendations = sorted(
                recommendations_qs,
                key=lambda x: es_ids.index(str(x.id)) if str(x.id) in es_ids else -1,
            )

            # Fallback: if no ES results
            if not recommendations:
                recommendations = list(
                    Article.objects.filter(published=True)
                    .exclude(id=article.id)
                    .order_by("?")[:4]
                )

        except Exception as e:
            print(f"Recommendation error: {e}")
            recommendations = list(
                Article.objects.filter(published=True)
                .exclude(id=article.id)
                .order_by("?")[:4]
            )

        cache.set(cache_key, recommendations, 60 * 60)  # cache 1 hour

    return render(
        request,
        "articles/detail.html",
        {
            "article": article,
            "content": content,
            "comments": approved_comments,
            "comment_form": comment_form,
            "recommendations": recommendations,
        },
    )


# Add Comment
# oct 11
# @login_required
# def add_comment(request, slug):
#     article = get_object_or_404(Article, slug=slug)
#     if request.method == "POST":
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.article = article
#             comment.author = request.user
#             comment.save()

#             # send notification
#             channel_layer = get_channel_layer()
#             async_to_sync(channel_layer.group_send)(
#                 f"user_{article.author.id}",
#                 {
#                     "type": "send_notification",
#                     "message": f'{request.user.username} commented on your article "{article.title}"',
#                 },
#             )

#             return redirect("articles:article_detail", slug=slug)
#     else:
#         form = CommentForm()

#     # For GET requests, render the article detail page with the form
#     content = articles_collection.find_one({"article_id": article.id})["content"]
#     approved_comments = article.comments.filter(approved=True)
#     return render(
#         request,
#         "articles/detail.html",
#         {
#             "article": article,
#             "content": content,
#             "comments": approved_comments,
#             "comment_form": form,
#         },
#     )

# comment on Oct 17
# @login_required
# def add_comment(request, slug):
#     article = get_object_or_404(Article, slug=slug)

#     # Restrict commenting on unpublished articles unless owner/superuser
#     if (
#         not article.published
#         and article.author != request.user
#         and not request.user.is_superuser
#     ):
#         return redirect("articles:article_list")

#     if request.method == "POST":
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             content = form.cleaned_data.get("content")
#             approved = not is_spam(content)  # Auto-moderation

#             comment = form.save(commit=False)
#             comment.article = article
#             comment.author = request.user
#             comment.approved = approved
#             comment.save()

#             # Send notification to article author
#             if article.author != request.user:  # prevent self-notification
#                 channel_layer = get_channel_layer()
#                 async_to_sync(channel_layer.group_send)(
#                     f"user_{article.author.id}",
#                     {
#                         "type": "send_notification",
#                         "message": f'{request.user.username} commented on your article "{article.title}"',
#                     },
#                 )

#             return redirect("articles:article_detail", slug=slug)
#     else:
#         form = CommentForm()

#     # GET request: render article detail page
#     content_doc = articles_collection.find_one({"article_id": article.id})
#     content = content_doc["content"] if content_doc else ""
#     approved_comments = article.comments.filter(approved=True)

#     return render(
#         request,
#         "articles/detail.html",
#         {
#             "article": article,
#             "content": content,
#             "comments": approved_comments,
#             "comment_form": form,
#         },
#     )


@login_required
def add_comment(request, slug):
    article = get_object_or_404(Article, slug=slug)

    # Restrict commenting on unpublished articles unless owner/superuser
    if (
        not article.published
        and article.author != request.user
        and not request.user.is_superuser
    ):
        return redirect("articles:article_list")

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data.get("content")
            parent_id = request.POST.get("parent_id")  # parent comment (optional)
            approved = not is_spam(content)  # Auto-moderation

            # Create comment
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.approved = approved
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id, article=article)
                    comment.parent = parent_comment
                except Comment.DoesNotExist:
                    pass  # Ignore invalid parent_id
            comment.save()

            # Send notification to article author (avoid self-notify)
            if article.author != request.user:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"user_{article.author.id}",
                    {
                        "type": "send_notification",
                        "message": f'{request.user.username} commented on your article "{article.title}"',
                    },
                )

            return redirect("articles:article_detail", slug=slug)
    else:
        form = CommentForm()

    # GET request: render article detail page
    mongo_doc = articles_collection.find_one({"article_id": article.id})
    content = mongo_doc["content"] if mongo_doc else ""
    approved_comments = article.comments.filter(approved=True).order_by("-created_at")

    return render(
        request,
        "articles/detail.html",
        {
            "article": article,
            "content": content,
            "comments": approved_comments,
            "comment_form": form,
        },
    )


@login_required
def add_reply(request, slug, comment_id):
    article = get_object_or_404(Article, slug=slug)
    parent_comment = get_object_or_404(Comment, id=comment_id)

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Comment.objects.create(
                article=article,
                author=request.user,
                content=content,
                parent=parent_comment,
                approved=True,
            )
        return redirect("articles:article_detail", slug=slug)


# Search
# Oct 2
# def search(request):
#     query = request.GET.get("q")
#     articles = (
#         Article.objects.filter(Q(title__icontains=query) | Q(category__name__icontains=query) | Q(tags__name__icontains=query))
#         if query
#         else Article.objects.all()
#     )
#     return render(request, "articles/list.html", {"articles": articles, "query": query})

# oct 9
# def search(request):
#     query = request.GET.get("q")
#     if query:
#         search = Search(index="articles").query(
#             "multi_match",
#             query=query,
#             fields=["title", "content", "category.name", "tags"],
#         )
#         response = search.execute()
#         article_ids = [hit.meta.id for hit in response]
#         articles = Article.objects.filter(id__in=article_ids)
#     else:
#         articles = Article.objects.all()
#     return render(request, "articles/list.html", {"articles": articles, "query": query})


def search(request):
    query = request.GET.get("q")
    articles = Article.objects.none()

    if query:
        # Search across multiple fields
        search = Search(index="articles").query(
            "multi_match",
            query=query,
            fields=[
                "title",
                "content",
                "category.name",
                "tags",
                "author.username",
            ],
        )

        response = search.execute()
        article_ids = [int(hit.meta.id) for hit in response.hits]
        articles = Article.objects.filter(id__in=article_ids)
    else:
        articles = Article.objects.all()

    return render(request, "articles/list.html", {"articles": articles, "query": query})


# Like
# 30 sept
# @login_required
# def toggle_like(request, slug):
#     article = get_object_or_404(Article, slug=slug)

#     like, created = Like.objects.get_or_create(article=article, user=request.user)
#     if not created:
#         like.delete()
#         liked = False
#     else:
#         liked = True
#     return JsonResponse({"liked": liked, "like_count": article.likes.count()})


@login_required
def toggle_like(request, slug):
    article = get_object_or_404(Article, slug=slug)

    like, created = Like.objects.get_or_create(article=article, user=request.user)

    if not created:
        # Already liked → remove it
        like.delete()
        liked = False
        action = "unliked"
    else:
        # New like
        liked = True
        action = "liked"

    # Send notification to article author
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{article.author.id}",
        {
            "type": "send_notification",
            "message": f'{request.user.username} {action} your article "{article.title}"',
        },
    )

    return JsonResponse({"liked": liked, "like_count": article.likes.count()})


# Dashboard
# oct 7
# def analytics_dashboard(request):
#     articles = Article.objects.all().order_by('-view_count')[:10]
#     total_users = User.objects.count()
#     total_articles = Article.objects.count()
#     toggle_like = Like.objects.count()
#     # total_comments = sum(article.comments.count() for article in articles)  # Total comments across all articles
#     return render(request, 'articles/analytics.html', {
#         'articles': articles,
#         'total_users': total_users,
#         'total_articles': total_articles,
#         'total_likes': toggle_like,
#         # 'total_comments': total_comments,
#     })


# Edit Article
@login_required
def article_edit(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.author != request.user:
        return redirect("articles:article_detail", slug=slug)  # Or raise 403

    mongo_content = (
        articles_collection.find_one({"article_id": article.id})["content"]
        if articles_collection.find_one({"article_id": article.id})
        else ""
    )

    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            article.updated_at = timezone.now()
            article.published = form.cleaned_data.get("published")
            article.save()
            form.save_m2m()  # Save many-to-many relationships like tags
            articles_collection.update_one(
                {"article_id": article.id},
                {"$set": {"content": form.cleaned_data["content"]}},
            )

            if article.published:
                article.author.check_expert_status()
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"user_{article.author.id}",
                    {
                        "type": "send_notification",
                        "message": f'Your article "{article.title}" was updated and published',
                    },
                )

            return redirect("articles:article_detail", slug=article.slug)
    else:
        form = ArticleForm(instance=article, initial={"content": mongo_content})
    return render(request, "articles/edit.html", {"form": form, "article": article})


# Delete Article
@login_required
def article_delete(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.author != request.user:
        return redirect("articles:article_list")
    if request.method == "POST":
        articles_collection.delete_one({"article_id": article.id})
        if article.featured_image:
            article.featured_image.delete()
        article.delete()
        return redirect("articles:article_list")
    return render(request, "articles/delete.html", {"article": article})


# Bookmark
@login_required
def toggle_bookmark(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if (
        not article.published
        and article.author != request.user
        and not request.user.is_superuser
    ):
        return JsonResponse({"error": "Article not published"}, status=403)
    bookmark, created = Bookmarks.objects.get_or_create(
        article=article, user=request.user
    )
    if not created:
        bookmark.delete()
    return JsonResponse(
        {"bookmarked": created, "bookmark_count": article.bookmarks.count()}
    )


# Report Comment
@login_required
def report_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == "POST":
        reason = request.POST.get("reason")
        CommentReport.objects.create(
            comment=comment, reporter=request.user, reason=reason
        )
        return redirect("articles:article_detail", slug=comment.article.slug)
    return render(request, "articles/report_comment.html", {"comment": comment})
