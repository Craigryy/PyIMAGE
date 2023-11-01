from django.urls import path, re_path
from django.contrib.auth.views import LogoutView
from .views import Home, ImageProcessing, DeleteImage, SaveProcessedImage, EffectsView

app_name = 'main'  # This sets the namespace

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('image/', ImageProcessing.as_view(), name='image'),
    path('effects/', EffectsView.as_view(), name='effects'),
    path('accounts/logout/', LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
    re_path(r'^image/(?P<id>[0-9]+)/delete/$', DeleteImage.as_view(), name='delete'),
    path('save-effects/', SaveProcessedImage.as_view(), name='save_effects'),
]
