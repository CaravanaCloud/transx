from django.http import HttpResponse
from django.shortcuts import render
from .forms import VideoForm


def home(request):
    context = {'greeting': 'salve mundao'}
    return render(request, 'transx_new/pages/home.html', context)

def video_upload(request):
    form = VideoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()

    context = {'form': form}

    return render(request, 'transx_new/pages/video_upload.html', context)
