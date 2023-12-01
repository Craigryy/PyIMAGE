from django.urls import path,re_path
from .views import HomeView, ImageProcessing, DeleteImage, SaveProcessedImage,custom_page_not_found, custom_server_error

# app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('image/', ImageProcessing.as_view(), name='image'),
    re_path(r'^image/(?P<id>[0-9]+)/delete/$', DeleteImage.as_view(), name='delete'),
    path('save-effects/', SaveProcessedImage.as_view(), name='save_effects'),
]