from django.db import models
from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')
db = client['datapro_content']
articles_collection = db['articles']
# Use this in views to store/retrieve article content
