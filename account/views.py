from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from account.forms import UserEditForm, ProfileEditForm, UserRegistrationForm
from account.models import Profile, Contact
from account.utils.decorators import staff_not_allowed
from account.utils.moderate import moderator_group_name
from blog_app.models import Post
from blog_app.utils.paginator import create_paginator


# Create your views here.


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            # Предварительно хэширует пароль перед сохранением
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(request, 'account/registration_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/registration.html', {'user_form': user_form})


@login_required
@staff_not_allowed
def edit(request):
    user_profile = request.user.profile
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=user_profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен')
        else:
            messages.error(request, 'Ошибка в обновлении профиля')

    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=user_profile)

    return render(request, 'account/edit.html', {'user_form': user_form, 'profile_form': profile_form})


def user_detail(request, username):
    user = get_object_or_404(get_user_model(), username=username, is_active=True)
    posts = user.posts.all()
    is_moderator = False

    if request.user.id != user.id:
        posts = posts.filter(status=Post.Status.PUBLISHED)
    elif request.user.groups.filter(name=moderator_group_name).exists():
        is_moderator = True
    else:
        posts = posts.order_by('-updated')


    posts = create_paginator(posts, request)
    return render(request,
                  'profile/detail.html',
                  {'user': user,
                   'posts': posts,
                   'moderator': is_moderator})


@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user
                )
                # create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})
