from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100)
    video = models.FileField(upload_to='videos/')