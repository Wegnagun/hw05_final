from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow, Comment


def index(request):
    """Вывод последних 10 постов"""
    post_list = Post.objects.select_related('author', 'group')
    paginator = Paginator(post_list, settings.MAX_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
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
    following = (request.user.is_authenticated and author.following.filter(
            user=request.user).exists())
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    posts = get_object_or_404(
        Post.objects.select_related('author', 'group').prefetch_related(
            'comments'), pk=post_id)
    author = posts.author
    form = CommentForm()
    following = (request.user.is_authenticated and author.following.filter(
        user=request.user).exists())
    context = {
        'author': author,
        'form': form,
        'posts': posts,
        'following': following
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
    if post.author != request.user:
        return redirect('posts:post_detail', post.pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)

    return render(request, 'posts/create_post.html', {'form': form,
                                                      'is_edit': True,
                                                      'post': post})


@login_required
def post_delete(request, post_id):
    posts = get_object_or_404(Post.objects.select_related('author'),
                              id=post_id)
    if posts.author != request.user:
        return redirect('posts:post_detail', posts.pk)
    posts.delete()
    return redirect('posts:index')


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


@login_required
def comment_delete(request, post_id, id):
    comment = Comment.objects.get(post_id=post_id, id=id)
    if request.user.id == comment.author_id:
        comment.delete()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Страница с постами уважаемых людей."""
    follower_post = Post.objects.filter(
        author__following__user=request.user).select_related('author', 'group')
    paginator = Paginator(follower_post, settings.MAX_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'posts/follow.html', {'page_obj': page_obj})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.username == author:
        return redirect('posts:profile', username=username)
    author.following.get_or_create(user=request.user)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    action_for_unfollow = author.following.filter(user=request.user)
    if action_for_unfollow.exists():
        action_for_unfollow.delete()
    return redirect('posts:profile', username=username)
