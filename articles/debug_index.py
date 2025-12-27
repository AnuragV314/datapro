# Create a debug script: debug_index.py
from django_elasticsearch_dsl.documents import Document

from .documents import ArticleDocument
from .models import Article

doc = ArticleDocument()
for article in Article.objects.all():
    try:
        doc.update([article], action='index', refresh=True)
        print(f"Indexed article {article.id}")
    except Exception as e:
        print(f"Failed to index article {article.id}: {str(e)}")