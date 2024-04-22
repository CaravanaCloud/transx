from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    context = {'greeting': 'salve mundao'}
    return render(request, 'uala.html', context)