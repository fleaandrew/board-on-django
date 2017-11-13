from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.urls import reverse

from . import models
from . import forms

# def home(request):
#     boards = models.Board.objects.all()
#     return render(request, 'forums/boards.html', {'boards': boards})

class BoardListView(ListView):
    model = models.Board
    context_object_name = 'boards'
    template_name = 'forums/boards.html'


# def board_topics(request, pk):
#     board = get_object_or_404(models.Board, pk=pk)
#     queryset = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
#     page = request.GET.get('page', 1)
#
#     paginator = Paginator(queryset, 20)
#
#     try:
#         topics = paginator.page(page)
#     except PageNotAnInteger:
#         topics = paginator.page(1)
#     except EmptyPage:
#         # probably the user tried to add a page number
#         # in the url, so we fallback to the last page
#         topics = paginator.page(paginator.num_pages)
#
#     return render(request, 'forums/board_topics.html', {'board': board, 'topics': topics})


class TopicListView(ListView):
    model = models.Topic
    context_object_name = 'topics'
    template_name = 'forums/board_topics.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(models.Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset

@login_required
def new_topic(request, pk):
    board = get_object_or_404(models.Board, pk=pk)
    if request.method == 'POST':
        form = forms.NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            post = models.Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect('forums:topic_posts', pk=board.pk, topic_pk=topic.pk)
    else:
        form = forms.NewTopicForm()
    return render(request, 'forums/new_topic.html', {'form': form, 'board':board})

# def topic_posts(request, pk, topic_pk):
#     topic = get_object_or_404(models.Topic, board__pk=pk, pk=topic_pk)
#     topic.views += 1
#     topic.save()
#     return render(request, 'forums/topic_posts.html', {'topic': topic})


class PostListView(ListView):
    model = models.Post
    context_object_name = 'posts'
    template_name = 'forums/topic_posts.html'
    paginate_by = 4

    def get_context_data(self, **kwargs):

        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True

        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(models.Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('-created_at')
        return queryset


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(models.Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = forms.PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

            topic_url = reverse('forums:topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )

            return redirect(topic_post_url)
    else:
        form = forms.PostForm()
    return render(request, 'forums/reply_topic.html', {'topic': topic, 'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = models.Post
    fields = ('message', )
    template_name = 'forums/edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('forums:topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)
