import markdown
from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe

from blog_app.models import Post

register = template.Library()  # быть допустимой библиотекой тегов


# имя функции - ее тег
# иначе, можно задать name=...
@register.simple_tag
def total_posts():
    return Post.objects.count()


@register.inclusion_tag('blog_app/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}
    # Должны возвращать словарь значений, которые используются для в контексте прорисовки


@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))  # по умолчанию Django не доверяет разметке и экранирует ее
