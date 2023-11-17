# models.py
import os
import hashlib
import requests
from django.contrib.auth.models import User
from django.db import models
from allauth.socialaccount.models import SocialAccount
from allauth.account.models import EmailAddress
from imagekit.models import ProcessedImageField, ImageSpecField
from imagekit.processors import ResizeToFit
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added

def delete_image(path):
    """
    Delete the image at the specified path.

    Parameters:
    - path (str): The path to the image file.
    """
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
        Meta class for specifying model options.
        """
        ordering = ('-modified_on',)

@receiver(pre_delete, sender=UploadImage)
def pre_delete_image_and_thumbnail(sender, instance, **kwargs):
    """
    Signal handler to delete image files and thumbnails on pre_delete.

    Parameters:
    - sender: The model class.
    - instance: The instance being deleted.
    """
    if instance.image:
        delete_image(instance.image.path)
    if instance.thumbnail:
        delete_image(instance.thumbnail.path)

class UserProfile(models.Model):
    """
    Represents a user profile.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_url = models.URLField(blank=True, null=True)

    def __str__(self):
        """
        Returns a string representation of the user profile.

        Returns:
        - str: The string representation.
        """
        return f"{self.user.username}'s profile"

    class Meta:
        db_table = 'user_profile'

    def is_email_verified(self):
        """
        Check if the user's email is verified.

        Returns:
        - bool: True if the email is verified, False otherwise.
        """
        email_addresses = EmailAddress.objects.filter(email=self.user.email)
        return email_addresses.exists() and email_addresses[0].verified

    def get_profile_image_url(self):
        """
        Get the URL of the user's profile image.

        Returns:
        - str: The profile image URL.
        """
        if self.avatar_url:
            return self.avatar_url

        social_account = SocialAccount.objects.filter(user=self.user).first()

        if social_account:
            if social_account.provider == 'google':
                return social_account.extra_data.get('picture', '')
            elif social_account.provider == 'facebook':
                # Fetch Facebook profile picture using the Graph API
                access_token = social_account.socialtoken_set.first().token
                fb_response = requests.get(
                    f'https://graph.facebook.com/v12.0/{social_account.uid}/picture',
                    params={'access_token': access_token, 'type': 'large'}
                )
                if fb_response.status_code == 200:
                    return fb_response.url

        return f"http://www.gravatar.com/avatar/{hashlib.md5(self.user.email.encode('utf-8')).hexdigest()}?s=40"

    User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
    
    @receiver(social_account_added)
    def update_user_avatar_and_populate_profile(sender, request, sociallogin, **kwargs):
        user = sociallogin.user

        if sociallogin.is_existing or not user.profile.avatar_url:
            account = sociallogin.account
            if account.provider == 'google':
                user.profile.avatar_url = account.extra_data.get('picture', '')
            elif account.provider == 'facebook':
                access_token = account.socialtoken_set.first().token
                fb_response = requests.get(
                    f'https://graph.facebook.com/v12.0/{account.uid}/picture',
                    params={'access_token': access_token, 'type': 'large'}
                )
                print(f"Facebook API Response: {fb_response.text}")  # Add this line for debugging

                if fb_response.status_code == 200:
                    user.profile.avatar_url = fb_response.url

        user.profile.save()
