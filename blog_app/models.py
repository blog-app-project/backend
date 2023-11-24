from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from pytils.translit import slugify
from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase

from account.models import Profile


# Создание собственного менеджера
class PublishedManager(models.Manager):
    def get_queryset(self):  # Набор queryset, который будет исполнен
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class ModeratedManager(models.Manager):
    def get_queryset(self):  # Набор queryset, который будет исполнен
        return super().get_queryset().filter(status=Post.Status.MODERATED)


class RussianTag(TagBase):
    def slugify(self, tag, i=None):
        slug = slugify(tag)
        if i is not None:
            slug += "_%d" % i
        return slug


class TaggedWhatever(GenericTaggedItemBase):
    tag = models.ForeignKey(
        RussianTag,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )


# Create your models here.
class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        MODERATED = 'MD', 'Moderated'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250,
                            blank=True)

    author = models.ForeignKey(get_user_model(),
                               on_delete=models.CASCADE,
                               related_name='posts'
                               )

    body = models.TextField()

    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.DRAFT)

    users_like = models.ManyToManyField(get_user_model(), related_name='posts_liked', blank=True)
    total_likes = models.PositiveIntegerField(default=0)

    tags = TaggableManager(blank=True, through=TaggedWhatever)

    # Хранение в обратном хронологическом порядке
    class Meta:
        ordering = ['-publish']  # - дефис = убыващий порядок
        indexes = [
            models.Index(fields=['-publish']),
            models.Index(fields=['-total_likes']),
        ]

    objects = models.Manager()  # Менеджер, применяемый по умолчанию
    published = PublishedManager()  # Если мы переопределяем менеджер, то дефолтный стирается
    moderated = ModeratedManager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    # Канонический адрес для модели
    def get_absolute_url(self):
        return reverse('blog_app:post_detail', args=(self.id,))


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(get_user_model(), related_name='comments_created', on_delete=models.CASCADE)

    total_likes = models.PositiveIntegerField(default=0)

    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    active = models.BooleanField(default=True)  # Деактивация неуместных комментариев
    moderator = models.BooleanField(default=False)  # Комментарии от модератора

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created'])
        ]

    def __str__(self):
        return f'Comment by {self.author.profile.blog_name} on {self.post}'
