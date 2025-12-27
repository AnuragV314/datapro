# import logging
# from django_elasticsearch_dsl import Document, fields
# from django_elasticsearch_dsl.registries import registry
# from .models import Article, Category
# from pymongo import MongoClient

# logger = logging.getLogger(__name__)

# @registry.register_document
# class ArticleDocument(Document):
#     title = fields.TextField()
#     category = fields.ObjectField(properties={'name': fields.TextField()})
#     tags = fields.ListField(fields.TextField())
#     content = fields.TextField()

#     class Index:
#         name = 'articles'

#     class Django:
#         model = Article
#         fields = []
#         related_models = [Category]

#     def prepare_content(self, instance):
#         try:
#             client = MongoClient('mongodb+srv://anuragpy:s6w1Zfl4DqVlrLqy@datapro.2nkidq5.mongodb.net/?retryWrites=true&w=majority&appName=datapro')
#             db = client['datapro_content']
#             doc = db.articles.find_one({'article_id': instance.id})
#             if doc and 'content' in doc:
#                 return doc['content']
#             logger.warning(f"No content found for article ID {instance.id}")
#             print(f"=====================>No content found for article ID {instance.id}")
#             return ''
#         except Exception as e:
#             print(f"=====================>Error fetching content for article ID {instance.id}: {str(e)}")
#             logger.error(f"Error fetching content for article ID {instance.id}: {str(e)}")
#             return ''

#     def prepare_tags(self, instance):
#         try:
#             return [tag.name for tag in instance.tags.all()]
#         except Exception as e:
#             print(f"=====================>Error preparing tags for article ID {instance.id}: {str(e)}")
#             logger.error(f"Error preparing tags for article ID {instance.id}: {str(e)}")
#             return []

#     def prepare_category(self, instance):
#         try:
#             return {'name': instance.category.name} if instance.category else {}
#         except Exception as e:
#             print(f"=====================>Error preparing category for article ID {instance.id}: {str(e)}")
#             logger.error(f"Error preparing category for article ID {instance.id}: {str(e)}")
#             return {}



import logging
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Article, Category
from pymongo import MongoClient

logger = logging.getLogger(__name__)

@registry.register_document
class ArticleDocument(Document):
    # title = fields.TextField()
    title = fields.TextField(
        analyzer="autocomplete",
        search_analyzer="standard"
    )
    category = fields.ObjectField(properties={'name': fields.TextField()})
    tags = fields.ListField(fields.TextField())
    content = fields.TextField()
    
    author = fields.ObjectField(properties={
        'username': fields.TextField(),
    })

    class Index:
        name = "articles"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "autocomplete": {
                        "tokenizer": "autocomplete_tokenizer",
                        "filter": ["lowercase"]
                    }
                },
                "tokenizer": {
                    "autocomplete_tokenizer": {
                        "type": "edge_ngram",
                        "min_gram": 2,
                        "max_gram": 20,
                        "token_chars": ["letter", "digit"]
                    }
                }
            }
        }

    class Django:
        model = Article
        fields = []
        related_models = [Category]

    def prepare(self, instance):
        """Override prepare to skip invalid documents."""
        data = super().prepare(instance)
        if not data.get('content'):  # Skip if content is empty
            logger.warning(f"Skipping indexing for article ID {instance.id} due to missing content")
            return {}   # Returning {} skips the document
        return data

    def prepare_content(self, instance):
        try:
            client = MongoClient('mongodb+srv://anuragpy:s6w1Zfl4DqVlrLqy@datapro.2nkidq5.mongodb.net/?retryWrites=true&w=majority&appName=datapro')
            db = client['datapro_content']
            doc = db.articles.find_one({'article_id': instance.id})
            if doc and 'content' in doc:
                return doc['content']
            logger.warning(f"No content found for article ID {instance.id}")
            print(f"=====================>No content found for article ID {instance.id}")
            return ''
        except Exception as e:
            print(f"=====================>Error fetching content for article ID {instance.id}: {str(e)}")
            logger.error(f"Error fetching content for article ID {instance.id}: {str(e)}")
            return ''

    def prepare_tags(self, instance):
        try:
            return [tag.name for tag in instance.tags.all()]
        except Exception as e:
            print(f"=====================>Error preparing tags for article ID {instance.id}: {str(e)}")
            logger.error(f"Error preparing tags for article ID {instance.id}: {str(e)}")
            return []

    def prepare_category(self, instance):
        try:
            return {'name': instance.category.name} if instance.category else {}
        except Exception as e:
            print(f"=====================>Error preparing category for article ID {instance.id}: {str(e)}")
            logger.error(f"Error preparing category for article ID {instance.id}: {str(e)}")
            return {}
        
    def prepare_author(self, instance):
        try:
            return {'username': instance.author.username} if instance.author else {}
        except Exception as e:
            logger.error(f"Error preparing author for article ID {instance.id}: {e}")
            return {}