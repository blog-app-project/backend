from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.mail import send_mail
from django.db.models import Count
from django.forms import model_to_dict
from django.http import Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from taggit.models import Tag

from blog_app.forms import EmailPostForm, CommentForm, SearchForm, CreatePostForm
from blog_app.models import Post, RussianTag
from blog_app.utils.paginator import create_paginator


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(RussianTag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])  # Связь многие-ко-многим - используем in
    posts = create_paginator(post_list, request)
    return render(request, 'blog_app/post/list.html', {'posts': posts,
                                                       'tag': tag,
                                                       'title': "Посты"})


def post_list_latest(request):
    latest_posts = Post.published.order_by('-publish')
    posts = create_paginator(latest_posts, request)
    return render(request, 'blog_app/post/list.html', {'section': 'new',
                                                       'posts': posts,
                                                       'tag': [],
                                                       'title': "Новое"})


def post_list_popular(request):
    latest_posts = Post.published.order_by('-total_likes')
    posts = create_paginator(latest_posts, request)
    return render(request, 'blog_app/post/list.html', {'section': 'best',
                                                       'posts': posts,
                                                       'tag': [],
                                                       'title': "Лучшее"})


@login_required
def post_list_from_subs(request):
    sub_posts_pks = request.user.following.all().values_list('posts', flat=True)
    post_list = Post.published.filter(pk__in=sub_posts_pks).order_by('-publish')
    posts = create_paginator(post_list, request)
    return render(request, 'blog_app/post/list.html', {'section': 'subs',
                                                       'posts': posts,
                                                       'tag': [],
                                                       'title': "Подписки"})


@login_required
def post_list_liked(request):
    post_list = request.user.posts_liked.all()
    posts = create_paginator(post_list, request)
    return render(request, 'blog_app/post/list.html', {'section': 'liked',
                                                       'posts': posts,
                                                       'tag': [],
                                                       'title': "Понравившееся"})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    if post.status != post.Status.PUBLISHED and post.author.id != request.user.id:
        raise Http404()

    post_tags_id = post.tags.values_list('id', flat=True)

    # получаем не одноэлементные кортежи [(1, ), (2, ), ...], а одиночные значения [1, 2, 3, ...]
    similar_posts = Post.objects.filter(tags__in=post_tags_id).exclude(id=post.id)

    similar_posts = similar_posts \
                        .annotate(same_tags=Count('tags')) \
                        .order_by('-same_tags', '-publish')[:4]

    comments = post.comments.filter(active=True)
    form = CommentForm()

    return render(request, 'blog_app/post/detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'similar_posts': similar_posts
    })


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():  # form.errors - список ошибок валидации
            cd = form.cleaned_data  # содержит только валидные поля
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, 'your_account@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog_app/post/share.html', {'post': post,
                                                        'form': form,
                                                        'sent': sent})


@login_required
@require_POST
def post_like(request):
    post_id = request.POST.get('id')
    action = request.POST.get('action')
    if post_id and action:
        try:
            post = Post.objects.get(id=post_id)
            if action == 'like':
                post.users_like.add(request.user)
            else:
                post.users_like.remove(request.user)  # Если объекта нет - ничего не произойдет
            return JsonResponse({'status': 'ok'})
        except Post.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:  # при get url будет содержать параметр query и им легко можно будет поделиться
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.published.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(rank__gte=0.3).order_by('-rank')
    return render(request, 'blog_app/post/search.html',
                  {'section': 'search',
                   'form': form,
                   'query': query,
                   'results': results})


@require_POST
@login_required
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None  # Хранение комментарного объекта при создании
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # подход видоизменения объекта до сохранения
        comment = form.save(commit=False)  # Экземпляр модели создается, но не сохраняется в бд
        # метод доступен только в ModelForm
        comment.post = post
        comment.author = request.user
        comment.save()

    return render(request, 'blog_app/post/comment.html', {'post': post,
                                                          'form': form,
                                                          'comment': comment})


@login_required
def post_create(request):
    if request.method == 'POST':
        form = CreatePostForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            messages.success(request, 'Пост сохранен как черновик')
            return redirect(request.user.profile.get_absolute_url())
    else:
        form = CreatePostForm(data=request.GET)
    return render(request, 'blog_app/post/create.html', {'form': form, 'user': request.user})


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author.id != request.user.id:
        raise Http404()
    post.delete()
    messages.success(request, 'Пост удален!')
    return redirect(request.user.profile.get_absolute_url())


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author.id != request.user.id:
        raise Http404()

    if request.method == 'POST':
        form = CreatePostForm(data=request.POST, instance=post)
        if form.is_valid():
            cd = form.cleaned_data
            new_post = form.save(commit=False)
            new_post.status = Post.Status.DRAFT
            new_post.save()
            messages.success(request, 'Пост сохранен')
    else:
        form = CreatePostForm(data=model_to_dict(post))
    return render(request, 'blog_app/post/edit.html', {'form': form, 'post': post, 'user': request.user})


@login_required
def post_publish(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author.id != request.user.id:
        raise Http404()

    post.status = post.Status.MODERATED
    post.save()
    messages.success(request, 'Пост отправлен на модерацию')
    return redirect(request.user.profile.get_absolute_url())
