from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404

from users.forms import ProfileForm
from .models import User
from articles.models import Article
from django.contrib.auth.decorators import login_required
# from .forms import UserForm

# for testing purposes
# def users(request):
#     users = User.objects.all()
#     return render(request, 'users/users.html', {'users': users})


def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    articles = Article.objects.filter(author=user)
    return render(request, 'users/profile.html', {'profile_user': user, 'articles': articles})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:user_profile', username=request.user.username)
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'users/edit.html', {'form': form})








