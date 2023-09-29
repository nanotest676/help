from django.contrib.auth import get_user_model
from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Post
        exclude = ('author',)


class UserForm(forms.ModelForm):
    class Meta:
        fields = ('email', 'first_name', 'last_name',)
        model = get_user_model()


class PasswordChangeForm(forms.ModelForm):
    class Meta:
        fields = ('password',)
        model = get_user_model()


class CommentForm(forms.ModelForm):
    class Meta:
        fields = ('text',)
        model = Comment
