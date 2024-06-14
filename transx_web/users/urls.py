from .import views
from django.urls import path # type: ignore
from django.urls import include # type: ignore

from users.apis import GoogleLoginApi, GoogleLoginRedirectApi

app_name = 'users'
urlpatterns = [
    #path('', include('django.contrib.auth.urls')),
    #path('login/', views.login, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('register/', views.register, name='register'),
    path("callback/", GoogleLoginApi.as_view(), name="callback-sdk"),
    path("redirect/", GoogleLoginRedirectApi.as_view(), name="redirect-sdk"),
]
