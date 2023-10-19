import os
from django.contrib.auth.models import User
from django.db import models
from allauth.socialaccount.models import SocialAccount
from allauth.account.models import EmailAddress
from imagekit.models import ProcessedImageField, ImageSpecField
from imagekit.processors import ResizeToFit
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import hashlib


# Utility function to delete an image
def _delete_image(path):
    if os.path.isfile(path):
        os.remove(path)

class UploadImage(models.Model):
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
        """
        Starting position 
        """
        ordering = ('-modified_on',)

    @receiver(pre_delete, sender=UploadImage)
def delete_image(sender, instance, *args, **kwargs):
    """
    Signal handler to delete image files on `pre_delete`.
    """
    if instance.image:
        _delete_image(instance.image.path)

@receiver(pre_delete, sender=UploadImage)
def delete_thumbnail(sender, instance, *args, **kwargs):
    """
    Signal handler to delete thumbnail images on `pre_delete`.
    """
    if instance.thumbnail:
        _delete_image(instance.thumbnail.path)


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
        Get the URL of the user's profile image.
        """
        if self.user.socialaccount_set.exists():
            social_account = self.user.socialaccount_set.first()

            if social_account.provider == 'facebook':
                # Facebook profile image URL
                return f"http://graph.facebook.com/{social_account.uid}/picture?width=40&height=40"
            elif social_account.provider == 'google':
                # Google profile image URL
                return social_account.extra_data.get('picture', '')

        # Fallback to Gravatar
        return f"http://www.gravatar.com/avatar/{hashlib.md5(self.user.email.encode('utf-8')).hexdigest()}?s=40"

    @property
    def profile(self):
        """
        Get or create the user's profile.
        """
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        return profile


