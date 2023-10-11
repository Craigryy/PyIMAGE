from __future__ import unicode_literals
from django.contrib.auth.admin import User
from django.db import models
import hashlib
import os
from allauth.socialaccount.models import SocialAccount
from allauth.account.models import EmailAddress


from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from django.dispatch import receiver
from pyIMAGE.settings import BASE_DIR
from imagekit.models import ProcessedImageField
from django.utils import timezone


class UploadedImage(models.Model):
    image = ProcessedImageField(upload_to='profile/%Y/%m/%d',
                                processors=[ResizeToFit(800, 600, False)],
                                format='JPEG',
                                options={'quality': 60})
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    edited = models.SmallIntegerField(default=0)
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = models.DateTimeField(auto_now=True)
    thumbnail = ImageSpecField(source='image',
                               processors=[ResizeToFit(120, 120, False)],
                               format='JPEG',
                               options={'quality': 100})

    class Meta:
        ordering = ('-modified_on',)


    def get_url(self):
        """
            Handle IOERR : This function checks if image exists,
            if it doesnt it deletes the record plus any thumbnail 
            that might exist
        """
        try:
            # get url if exists

            if os.path.isimage(BASE_DIR + self.image.url):
                return self.thumbnail.url
            # if the path is not a image do house cleaning
            self.delete()
            return None
        except IOError:
            return None


from django.contrib.auth.models import User

class Userprofile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    def __unicode__(self):
        return "{}'s profile".format(self.user.username)

    class Meta:
        db_table = 'user_profile'

    def account_verified(self):
        if self.user.is_authenticated:
            result = EmailAddress.objects.filter(email=self.user.email)
            if len(result):
                return result[0].verified
        return False

    def profile_image_url(self):
        fb_uid = SocialAccount.objects.filter(
            user_id=self.user.id, provider='facebook')
        if len(fb_uid):
            return "http://graph.facebook.com/{}/picture?\
                    width=40&height=40".format(fb_uid[0].uid)
        return "http://www.gravatar.com/avatar/{}?s=40".format(
            hashlib.md5(self.user.email).hexdigest())



User.profile = property(lambda u: Userprofile.objects.get_or_create(user=u)[0])


def _delete_image(path):
    """Deletes image from imagesystem."""
    if os.path.isimage(path):
        os.remove(path)


@receiver(models.signals.pre_delete, sender=UploadedImage)
def delete_image(sender, instance, *args, **kwargs):
    """Delete image files on `post_delete`."""
    if instance.image:
        _delete_image(instance.image.path)


@receiver(models.signals.pre_delete, sender=UploadedImage)
def delete_thumbnail(sender, instance, *args, **kwargs):
    """Delete thumbnail images on `post_delete`."""
    if instance.thumbnail:
        _delete_image(instance.thumbnail.path)
