from django import forms
from django.forms import Form

from blog_app.models import Comment, Post


class EmailPostForm(forms.Form):
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)  # use <textarea>


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'tags']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']


class SearchForm(forms.Form):
    query = forms.CharField()
