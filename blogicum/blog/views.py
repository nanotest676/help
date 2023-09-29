from datetime import datetime

from django.utils import timezone
from blog.models import Category, Post
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, PasswordChangeForm, PostForm, UserForm
from .models import Category, Comment, Post, User
from .utils import filter_published, select_post_objects

SUM_POSTS = 10


class Index(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by: int = SUM_POSTS

    def get_queryset(self):
        return filter_published(
            select_post_objects(Post).filter(
                category__is_published=True,
                pub_date__lte=datetime.now(),
                is_published__exact=True
                )
        ).order_by('-pub_date')


def post_detail(request, id):
    template = 'blog/detail.html'
    post_detail = get_object_or_404(
        Post.objects.select_related('category')
        .prefetch_related(
            'location'
        ).filter(
            category__is_published=True,
            pub_date__lte=timezone.now(),
            is_published=True
        ), id=id
    )
    context = {'post': post_detail}
    return render(request, template, context)

def category_posts(request, category_slug):
    template = 'blog/category.html'
    category_posts = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )
    list = Post.objects.filter(
        category__exact=category_posts,
        category=category_posts,
        pub_date__lte=timezone.now(),
        is_published=True
    )
    context = {'category': category_posts, 'post_list': list}
    return render(request, template, context)


class CreatePost(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create_post.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={
                'username': self.request.user.get_username()
            }
        )


class DeletePost(LoginRequiredMixin, DeleteView):
    template_name = 'blog/create_post.html'
    success_url = reverse_lazy('blog:index')
    
    def sending(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect(
                'blog:post_detail',
                self.kwargs.get('post_id')
            )
        return super().dispatch(request, *args, **kwargs)


class NewComment(LoginRequiredMixin, CreateView):
    blog_post = None
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.blog_post
        return super().form_valid(form)


    def get_object(self):
        return get_object_or_404(
            Comment,
            pk=self.kwargs.get('comment_id'),
            post=Post.objects.get(pk=self.kwargs.get('post_id')),
            author=self.request.user)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs.get('post_id')}
        )
    
class DeleteComment(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment_form.html'

    def get_object(self, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return get_object_or_404(
            Comment,
            pk=self.kwargs.get('comment_id'),
            post=post,
            author=self.request.user)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs.get('post_id')}
        )


class EditComment(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect('blog:post_detail', post_id=obj.id)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, **kwargs):
        if not self.request.user.is_authenticated:
            raise Http404
        return get_object_or_404(
            Comment,
            pk=self.kwargs.get('comment_id'),
            post=Post.objects.get(pk=self.kwargs.get('post_id')),
            author=self.request.user
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs.get('post_id')}
        )




class Profile(ListView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by: int = SUM_POSTS

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )

        if self.author != self.request.user:
            return filter_published(select_post_objects(Post).filter(
                author=self.author,
            )).order_by(
                '-pub_date')

        return select_post_objects(Post).filter(
            author=self.author
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        context['user'] = self.request.user
        return context


class EditProfile(LoginRequiredMixin, UpdateView):
    form_class = UserForm
    model = User
    template_name = 'blog/user.html'
    user = None

    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(
            User,
            username=kwargs['username']
        )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(
            User,
            username=self.user.get_username(),
        )

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.user.get_username()}
        )


class PasswordChange(EditProfile):
    form_class = PasswordChangeForm
    model = User
    template_name = 'registration/password_reset_form.html'