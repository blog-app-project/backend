from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType

from account.models import Profile
from blog_app.models import Post

moderator_group_name = 'moderators'
moderator_permission_codename = "can_moderate"
moderator_permission_name = f"Can Moderate Posts"


def create_permission(codename: str, name: str):
    content_type = ContentType.objects.get_for_model(Post)
    permission, _ = Permission.objects.get_or_create(
        codename=codename,
        name=name,
        content_type=content_type,
    )
    return permission


def create_moderate_group():
    new_group, _ = Group.objects.get_or_create(name=moderator_group_name)

    permission = create_permission(moderator_permission_codename, moderator_permission_name)

    new_group.permissions.add(permission)
    print(f"Added permission {moderator_permission_name} to group {moderator_group_name}")


def create_moderator(email: str, **kwargs):
    username = kwargs.get('username')
    password = kwargs.get('password')

    if username is None:
        moder_id = get_user_model().objects.filter(username__startswith="moderator").count() + 1
        username = f"moderator{moder_id}"
    if password is None:
        password = get_user_model().objects.make_random_password()

    user = get_user_model().objects.create_user(username=username, email=email, password=password, **kwargs)

    Profile.objects.create(user=user)

    moderators_group = Group.objects.get(name=moderator_group_name)
    user.groups.add(moderators_group)

    print(f"Moderator's account is created:")
    print(f"\tUsername: {username}")
    print(f"\tEmail: {email}")
    print(f"\tPassword: {password}")
