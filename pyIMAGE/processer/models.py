from django.contrib.auth.models import User
from django.db import models
import hashlib
import os
from allauth.socialaccount.models import SocialAccount
from allauth.account.models import EmailAddress
from imagekit.models import ProcessedImageField, ImageSpecField
from imagekit.processors import ResizeToFit
from django.dispatch import receiver
from django.utils import timezone

# Utility function to delete an image
def _delete_image(path):
    if os.path.isfile(path):
        os.remove(path)

class UploadedImage(models.Model):
    """
    Represents an uploaded image.
    """
    image = ProcessedImageField(
        upload_to='profile/%Y/%m/%d',
        processors=[ResizeToFit(800, 600, False)],
        format='JPEG',
        options={'quality': 60}
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    edited = models.SmallIntegerField(default=0)
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = models.DateTimeField(auto_now=True)
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFit(120, 120, False)],
        format='JPEG',
        options={'quality': 100}
    )

    class Meta:
        ordering = ('-modified_on',)

    def get_url(self):
        """
        Get the URL of the image's thumbnail.
        """
        try:
            # Check if the image exists
            if os.path.isfile(self.image.path):
                return self.thumbnail.url
            # If the image doesn't exist, do house cleaning
            self.delete()
            return None
        except IOError:
            return None

class UserProfile(models.Model):
    """
    Represents a user profile.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        db_table = 'user_profile'

    def account_verified(self):
        """
        Check if the user's email is verified.
        """
        if self.user.is_authenticated:
            result = EmailAddress.objects.filter(email=self.user.email)
            return len(result) > 0 and result[0].verified

    def profile_image_url(self):
        """
        Get the URL of the user's profile image (Facebook or Gravatar).
        """
        fb_uid = SocialAccount.objects.filter(
            user_id=self.user.id, provider='facebook'
        )
        if len(fb_uid):
            return f"http://graph.facebook.com/{fb_uid[0].uid}/picture?width=40&height=40"
        return f"http://www.gravatar.com/avatar/{hashlib.md5(self.user.email.encode('utf-8')).hexdigest()}?s=40"

# Connect the UserProfile to the User model
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

@receiver(models.signals.pre_delete, sender=UploadedImage)
def delete_image(sender, instance, *args, **kwargs):
    """
    Signal handler to delete image files on `pre_delete`.
    """
    if instance.image:
        _delete_image(instance.image.path)

@receiver(models.signals.pre_delete, sender=UploadedImage)
def delete_thumbnail(sender, instance, *args, **kwargs):
    """
    Signal handler to delete thumbnail images on `pre_delete`.
    """
    if instance.thumbnail:
        _delete_image(instance.thumbnail.path)
