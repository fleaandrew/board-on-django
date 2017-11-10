from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from . import models
from . import forms

def home(request):
    boards = models.Board.objects.all()
    return render(request, 'forums/boards.html', {'boards': boards})
    # return HttpResponse('Hello world!')

def board_topics(request, pk):
    board = get_object_or_404(models.Board, pk=pk)
    topics = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    return render(request, 'forums/board_topics.html', {'board': board, 'topics': topics})

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

def topic_posts(request, pk, topic_pk):
    # posts = models.Post.objects.filter(topic__pk=topic_pk)
    topic = get_object_or_404(models.Topic, board__pk=pk, pk=topic_pk)
    topic.views += 1
    topic.save()
    return render(request, 'forums/topic_posts.html', {'topic': topic})

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
            return redirect('forums:topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = forms.PostForm()
    return render(request, 'forums/reply_topic.html', {'topic': topic, 'form': form})
