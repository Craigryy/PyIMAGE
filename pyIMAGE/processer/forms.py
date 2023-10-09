# import os
# import requests

# from django import forms
# from django.contrib.auth.models import User

# from .models import UploadedImage

# from allauth.socialaccount.forms import SignupForm


# class FacebookLoginForm(SignupForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['username'].widget.attrs['style'] = 'display:none;'  # Hide username field

#     def save(self, request):
#         # Create a new user or get the existing user
#         user = super().save(request)
#         return user



# class ImageUploadForm(forms.ModelForm):
#     class Meta:
#         model = UploadedImage
#         fields = ['image', 'title', 'effects']


# def get_credentials(access_token):
#     app_id = os.getenv("FACEBOOK_APP_ID"),
#     app_secret = os.getenv("FACEBOOK_APP_SECRET"),
#     user_short_token = access_token
#     access_token_url = f"https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id[0]}&client_secret={app_secret[0]}&fb_exchange_token={user_short_token}"

#     facebook_request = requests.get(access_token_url)
#     access_token_info = facebook_request.json()

#     user_long_token = access_token_info['access_token']
#     token_expiry_time = access_token_info['expires_in']

#     return (user_long_token, token_expiry_time)


# class FacebookAuthForm(forms.Form):
#     """
#     Form for validating and saving Facebook
#     user authentication data. Returns the
#     existing or created user.
#     """

#     id = forms.CharField()
#     email = forms.EmailField()
#     first_name = forms.CharField()
#     last_name = forms.CharField()
#     photo = forms.CharField(required=False)
#     accessToken = forms.CharField(required=False)

#     def save(self):
#         """
#         gets returns the social user with the form data.
#         creates one if it does not already exists.
#         """
#         data = self.cleaned_data
#         user = None

#         # make call to graphAPI to get long-lived access token
#         user_access_token, token_expiry_time = get_credentials(data['accessToken'])

#         try:
#             # get associated user if it exists:
#             social_id = data['id']
#             social_profile = UploadedImage.objects.get(
#                 provider=UploadedImage.FACEBOOK,
#                 social_id=social_id,
#             )
#             user = social_profile.user

#         except UploadedImage.DoesNotExist:
#             # Create the user:
#             user = User(
#                 username=data['id'],
#                 first_name=data['first_name'],
#                 last_name=data['last_name']
#             )
#             user.save()

#             # Create the user's social_profile:
#             social_profile = UploadedImage(
#                 provider=UploadedImage.FACEBOOK,
#                 social_id=data['id'],
#                 photo=data['photo'],
#                 user_access_token = user_access_token,
#                 user = user,
#             )
#             social_profile.save()

#         user.backend = 'django.contrib.auth.backends.ModelBackend'
#         return (user, token_expiry_time)