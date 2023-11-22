from django.urls import path

from blog_app import views

app_name = 'blog_app'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('<int:post_id>/comment/', views.post_comment, name='post_comment'),
    path('search/', views.post_search, name='post_search'),

    path('create/', views.post_create, name='create'),
    path('<int:post_id>/delete/', views.post_delete, name='delete'),
    path('<int:post_id>/edit/', views.post_edit, name='edit'),
    path('<int:post_id>/publish/', views.post_publish, name='publish'),
]

# slug - строка содержащая только буквы цифры и -, _
# re_path - сложные шаблоны URL адресов с использование RegEx