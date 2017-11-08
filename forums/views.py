from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
# Create your views here.

from . import models
from . import forms

def home(request):
    boards = models.Board.objects.all()
    return render(request, 'forums/boards.html', {'boards': boards})
    # return HttpResponse('Hello world!')

def board_topics(request, pk):
    board = get_object_or_404(models.Board, pk=pk)
    #topics = models.Topic.objects.filter(board__pk=pk)
    return render(request, 'forums/board_topics.html', {'board': board})

def new_topic(request, pk):
    board = get_object_or_404(models.Board, pk=pk)
    user = User.objects.first()
    if request.method == 'POST':
        form = forms.NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = user
            topic.save()
            post = models.Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=user
            )
            return redirect('forums:board_topics', pk=board.pk)
    else:
        form = forms.NewTopicForm()
    return render(request, 'forums/new_topic.html', {'form': form, 'board':board})
