from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # testing purposes
    # path('', views.users, name='users'),
    
    # User profile page
    path('edit/', views.profile_edit, name='profile_edit'),
    path('<str:username>/', views.user_profile, name='user_profile'),
]
