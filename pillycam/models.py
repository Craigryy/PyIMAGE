import os
import hashlib
from django.contrib.auth.models import User
from django.db import models
from allauth.socialaccount.models import SocialAccount
from allauth.account.models import EmailAddress
from imagekit.models import ProcessedImageField, ImageSpecField
from imagekit.processors import ResizeToFit
from django.utils import timezone
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from allauth.socialaccount.signals import social_account_added

# Utility function to delete an image file
def delete_image(path):
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
def pre_delete_image(sender, instance, **kwargs):
    """
    Signal handler to delete image files on pre_delete.
    """
    if instance.image:
        delete_image(instance.image.path)

@receiver(pre_delete, sender=UploadImage)
def pre_delete_thumbnail(sender, instance, **kwargs):
    """
    Signal handler to delete thumbnail images on pre_delete.
    """
    if instance.thumbnail:
        delete_image(instance.thumbnail.path)

class UserProfile(models.Model):
    """
    Represents a user profile.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        db_table = 'user_profile'

    def is_email_verified(self):
        """
        Check if the user's email is verified.
        """
        if self.user.is_authenticated:
            email_addresses = EmailAddress.objects.filter(email=self.user.email)
            return email_addresses.exists() and email_addresses[0].verified

    def get_profile_image_url(self):
        """
        Get the URL of the user's profile image.
        """
        if self.avatar_url:
            return self.avatar_url
        else:
            social_account = SocialAccount.objects.filter(user=self.user).first()

            if social_account:
                if social_account.provider == 'facebook':
                    return f"http://graph.facebook.com/{social_account.uid}/picture?width=40&height=40"
                elif social_account.provider == 'google':
                    return social_account.extra_data.get('picture', '')

            # Fallback to Gravatar
            return f"http://www.gravatar.com/avatar/{hashlib.md5(self.user.email.encode('utf-8')).hexdigest()}?s=40"

    User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

@receiver(social_account_added)
def update_user_avatar(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    if sociallogin.is_existing:
        return
    if not user.profile.avatar_url:
        if sociallogin.account.provider == 'facebook':
            user.profile.avatar_url = f"http://graph.facebook.com/{sociallogin.account.uid}/picture?width=40&height=40"
        elif sociallogin.account.provider == 'google':
            user.profile.avatar_url = sociallogin.account.extra_data.get('picture', '')
    user.profile.save()

@receiver(social_account_added)
def populate_profile(sender, request, sociallogin, user, **kwargs):
    provider = sociallogin.account.provider
    user_data = user.socialaccount_set.filter(provider=provider)[0].extra_data

    if provider == 'facebook':
        picture_url = "http://graph.facebook.com/" + sociallogin.account.uid + "/picture?type=large"
        email = user_data['email']
        first_name = user_data['first_name']
    elif provider == 'linkedin':
        picture_url = user_data['picture-urls']['picture-url']
        email = user_data['email-address']
        first_name = user_data['first-name']
    elif provider == 'twitter':
        picture_url = user_data['profile_image_url']
        picture_url = picture_url.rsplit("_", 1)[0] + "." + picture_url.rsplit(".", 1)[1]
        email = user_data['email']
        first_name = user_data['name'].split()[0]

    user.profile.avatar_url = picture_url
    user.profile.email_address = email
    user.profile.first_name = first_name
    user.profile.save()
