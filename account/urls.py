from django.urls import path, include

from account import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('user/edit/', views.edit, name='edit'),

    path('blog/follow/', views.user_follow, name='user_follow'),
    path('blog/<username>/', views.user_detail, name='user_detail')
]