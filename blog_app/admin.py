from django.contrib import admin

from blog_app.models import Post, Comment


@admin.register(Post)  # выполняет ту же функцию, что и admin.site.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = ['status', 'created', 'publish', 'author']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title', )}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['-status', '-publish']

    fieldsets = [
        ("Post info", {"fields": ["title", "slug", "status", "body", "author", "tags"]}),
        ("Dates", {"fields": ["publish"]}),
    ]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['author', 'body']

# Register your models here.

