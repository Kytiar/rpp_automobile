from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.db import models  # Добавьте эту строку
from .models import Post, Category, Author, UserProfile, Like  # Убедитесь, что все модели импортированы
from .forms import PostForm, RegisterForm
from .permissions import admin_or_author_required, admin_author_or_editor_required
from django.shortcuts import redirect

def base_context(request):
    categories = Category.objects.all()
    return {'categories': categories}


def role_required(*roles):
    def decorator(view_func):
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if not hasattr(request.user, 'profile'):
                raise PermissionDenied
            if request.user.profile.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator


def home(request):
    posts = Post.objects.select_related('author').prefetch_related('categories').all()[:5]
    return render(request, 'blog/home.html', {'posts': posts})


def post_list(request):
    posts = Post.objects.select_related('author__user').prefetch_related('categories').all()
    context = base_context(request)
    context.update({'posts': posts})
    return render(request, 'blog/post_list.html', context)


def post_detail(request, pk):
    post = get_object_or_404(
        Post.objects.select_related('author__user').prefetch_related('categories'),
        pk=pk
    )
    is_liked = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(user=request.user, post=post).exists()

    context = base_context(request)
    context.update({
        'post': post,
        'is_liked': is_liked
    })
    return render(request, 'blog/post_detail.html', context)


# blog/views.py
@role_required('admin', 'editor', 'author')
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, user=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user.author
            post.save()
            form.save_m2m()
            return redirect('blog:post_detail', pk=post.pk)  # Добавляем пространство имен 'blog:'
    else:
        form = PostForm(user=request.user)
    return render(request, 'blog/post_form.html', {'form': form})


# blog/views.py

@admin_author_or_editor_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Проверка прав: админ, автор поста или редактор
    if not (request.user.profile.role == 'admin' or
            request.user == post.author.user or
            request.user.profile.role == 'editor'):
        raise PermissionDenied

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post, user=request.user)

    return render(request, 'blog/post_form.html', {'form': form})


@admin_or_author_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Проверка прав: только админ или автор поста
    if not (request.user.profile.role == 'admin' or
            request.user == post.author.user):
        raise PermissionDenied

    if request.method == 'POST':
        post.delete()
        return redirect('blog:post_list')

    return render(request, 'blog/post_confirm_delete.html', {'post': post})

@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'likes_count': post.likes.count(),
            'is_liked': created
        })
    return redirect('blog:post_detail', pk=post.pk)  # Добавляем пространство имен 'blog:'

@login_required
# blog/views.py
def category_list(request):
    categories = Category.objects.annotate(post_count=models.Count('posts'))
    context = base_context(request)
    context.update({'categories': categories})
    return render(request, 'blog/category_list.html', context)


def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    posts = Post.objects.filter(categories=category).select_related('author__user')

    context = base_context(request)
    context.update({
        'category': category,
        'posts': posts
    })
    return render(request, 'blog/category_detail.html', context)


# blog/views.py
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            # Создаем профиль пользователя, если он еще не существует
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user, role=form.cleaned_data['role'])

            # Создаем автора, если он еще не существует
            if not hasattr(user, 'author'):
                Author.objects.create(user=user)

            login(request, user)
            return redirect('blog:post_list')
    else:
        form = RegisterForm()
    return render(request, 'blog/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('blog:post_list')  # Изменено с 'home' на 'blog:post_list'
    else:
        form = AuthenticationForm()
    return render(request, 'blog/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('blog:post_list')