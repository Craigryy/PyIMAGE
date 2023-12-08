from django.urls import path, re_path
from .views import HomeView, ImageProcessingView, DeleteImage, SaveProcessedImage

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    re_path(r'^image/(?P<id>[0-9]+)/delete/$', DeleteImage.as_view(), name='delete'),
    path('save-effects/', SaveProcessedImage.as_view(), name='save_effects'),
    path('apply_effect/', ImageProcessingView.as_view(), name='apply_effect'),
]
