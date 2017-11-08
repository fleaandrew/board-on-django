from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

from . import models

def home(request):
    boards = models.Board.objects.all()
    return render(request, 'forums/boards.html', {'boards': boards})
    # return HttpResponse('Hello world!')
