# from django.urls import path
# from . import views
# from allauth.account.views import SignupView, LogoutView
# from allauth.account.views import LoginView

# app_name = 'pillycam' 

# urlpatterns = [
#     path('effects/', views.EffectsView.as_view(), name='effects'),
#     path('home/', views.Home.as_view(), name='home'),
#     path('dashboard/', views.dashboard, name='dashboard'),
#     path('image-processing/', views.ImageProcessing.as_view(), name='image_processing'),
#     path('save-processed-image/', views.SaveProcessedImage.as_view(), name='save_processed_image'),
#     path('login/', LoginView.as_view(), name='custom_login'),  # Custom login view
#     path('logout/', LogoutView.as_view(), name='account_logout'),  # Logout view
#     path('signup/', SignupView.as_view(), name='account_signup'),  # Signup view
# ]


from django.urls import path, re_path
from django.contrib.auth.views import LogoutView
from .views import Home, ImageProcessing, DeleteImage, SaveProcessedImage, Effects

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('image/', ImageProcessing.as_view(), name='image'),
    path('effects/', Effects.as_view(), name='effects'),
    path('accounts/logout/', LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
    re_path(r'^image/(?P<id>[0-9]+)/delete/$', DeleteImage.as_view(), name='delete'),
    path('save-effects/', SaveProcessedImage.as_view(), name='save_effects'),
]
