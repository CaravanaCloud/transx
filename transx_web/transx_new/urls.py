from django.urls import path
from .import views


app_name = 'transx_new'

urlpatterns = [
    # Homepage
    path('', views.index, name='index'),
]