from .import views
from django.urls import path
from django.urls import include

app_name = 'users'
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('log_out/', views.log_out, name='log_out'),
    path('register/', views.register, name='register'),
]
