from django.shortcuts import render
from .models import ArticleView
from articles.models import Article, Comment, Like
from users.models import User
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count



def is_superuser(user):
    return user.is_superuser


# oct 7 2025: Temporarily disabling the analytics dashboard view
# @user_passes_test(is_superuser)
# def analytics_dashboard(request):
#     # Total article views
#     total_views = ArticleView.objects.count()

#     # Views in the last 7 days
#     one_week_ago = timezone.now() - timedelta(days=7)
#     weekly_views = ArticleView.objects.filter(view_date__gte=one_week_ago).count()

#     # Top 5 most viewed articles
#     top_articles = (ArticleView.objects
#                     .values('article')
#                     .annotate(view_count=Count('id'))
#                     .order_by('-view_count')[:5])

#     top_articles_details = []
#     for entry in top_articles:
#         article = Article.objects.get(id=entry['article'])
#         top_articles_details.append({
#             'article': article,
#             'view_count': entry['view_count']
#         })

#     # Recent views with pagination
#     recent_views_list = ArticleView.objects.select_related('article', 'user').order_by('-view_date')
#     paginator = Paginator(recent_views_list, 10)  # Show 10 views per page
#     page_number = request.GET.get('page')
#     recent_views = paginator.get_page(page_number)

#     context = {
#         'total_views': total_views,
#         'weekly_views': weekly_views,
#         'top_articles': top_articles_details,
#         'recent_views': recent_views,
#     }
#     return render(request, 'analytics/dashboard.html', context)



def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def analytics_dashboard(request):
    # Basic metrics
    total_articles = Article.objects.count()
    total_views = ArticleView.objects.count()
    total_likes = Like.objects.count()
    total_comments = Comment.objects.count()
    active_users = User.objects.filter(is_active=True).count()

    # Views over last 30 days
    last_30_days = timezone.now() - timedelta(days=30)
    views_by_day = ArticleView.objects.filter(view_date__gte=last_30_days).extra(
        select={'day': "DATE(view_date)"}
    ).values('day').annotate(count=Count('id')).order_by('day')

    # Top articles by views
    top_articles = Article.objects.annotate(
        total_views=Count('title')
    ).order_by('-view_count')[:10]

    context = {
        'total_articles': total_articles,
        'total_views': total_views,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'active_users': active_users,
        'views_by_day': list(views_by_day),
        'top_articles': top_articles,
    }
    return render(request, 'analytics/dashboard.html', context)



