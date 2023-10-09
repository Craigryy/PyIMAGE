from django.db import models
from django.contrib.auth.models import User

class UploadedImage(models.Model):
   
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    social_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    image = models.ImageField(upload_to='uploaded_images/')
    title = models.CharField(max_length=100, blank=True)
    effects = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.title} ({self.user.username})'
