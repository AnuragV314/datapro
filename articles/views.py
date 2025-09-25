from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404

def articles(request):
    return render(request, 'articles/articles.html')
