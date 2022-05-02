from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Post, Group, User


@cache_page(20)
def index(request):
    """Вывод последних 10 постов"""
    posts = Post.objects.select_related('author', 'group')
    paginator = Paginator(posts, settings.MAX_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'index': 'Последние обновления на сайте',
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Вывод последних 10 постов конкретной группы - <slug>"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    paginator = Paginator(posts, settings.MAX_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post = author.posts.select_related('group')
    paginator = Paginator(post, settings.MAX_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'page_obj': page_obj,
        'posts': post
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author',
                                                         'group'), pk=post_id)
    comments = post.comments.select_related('author')
    author = post.author
    form = CommentForm(request.POST or None)
    context = {
        'author': author,
        'posts': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author'), id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if post.author != request.user:
        return redirect('posts:post_detail', post.pk)

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)

    return render(request, 'posts/create_post.html', {'form': form,
                                                      'is_edit': True,
                                                      'posts': post})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)