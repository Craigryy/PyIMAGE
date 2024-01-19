from django.urls import path
from .views import (
    HomeView,
    PhotoAppView,
    DeletePhotoView,
    EffectImageView,
)

app_name = 'main'  # This sets the namespace

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('photos/', PhotoAppView.as_view(), name='mainpage'),
    path('delete/', DeletePhotoView.as_view(), name='delete'),
    path('addeffects/', EffectImageView.as_view(), name='addeffects'),
]


