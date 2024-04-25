from django.urls import path
from .import views


app_name = 'transx_new'

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),
    path('transx/video/', views.video_upload, name='video_upload'),
]