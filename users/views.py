from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from .models import User
from .forms import UserForm

def users(request):
    users = User.objects.all()
    return render(request, 'users/users.html', {'users': users})

def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:users')
    else:
        form = UserForm()
    return render(request, 'users/user_form.html', {'form': form})

def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users:users')
    else:
        form = UserForm(instance=user)
    return render(request, 'users/user_form.html', {'form': form})

def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('users:users')
    return render(request, 'users/user_confirm_delete.html', {'user': user})

