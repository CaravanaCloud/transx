from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Video(models.Model):

    class SpokenLanguage(models.TextChoices):
        ENGLISH = 'EN', 'English'
        SPANISH = 'ES', 'Spanish'
        PORTUGUESE = 'PT', 'Portuguese'
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100)
    video = models.FileField(upload_to='videos/')
    spoken_language = models.CharField(
        max_length=50, choices=SpokenLanguage.choices, default=SpokenLanguage.ENGLISH)