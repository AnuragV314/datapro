from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.users, name='users'),
    path('create/', views.user_create, name='user_create'),
    path('<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('<int:pk>/delete/', views.user_delete, name='user_delete'),
]
