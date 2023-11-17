# from django.urls import path, re_path
# from django.contrib.auth.views import LogoutView
# from .views import HomeView, ImageProcessing, DeleteImage, SaveProcessedImage, EffectsView

# app_name = 'main'  # This sets the namespace

# urlpatterns = [
#     path('', HomeView.as_view(), name='home'),
#     path('image/', ImageProcessing.as_view(), name='image'),
#     path('effects/', EffectsView.as_view(), name='effects'),
#     path('accounts/logout/', LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
#     re_path(r'^image/(?P<id>[0-9]+)/delete/$', DeleteImage.as_view(), name='delete'),
#     path('save-effects/', SaveProcessedImage.as_view(), name='save_effects'),
# ]

from django.urls import path
from .views import HomeView, UploadImageView, ViewUploadedPicturesView, DeleteAllPhotosView, ApplyFilterView

app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('upload/', UploadImageView.as_view(), name='upload_image'),
    path('view/', ViewUploadedPicturesView.as_view(), name='view_uploaded_pictures'),
    path('delete-all/', DeleteAllPhotosView.as_view(), name='delete_all_photos'),
    path('apply-filter/', ApplyFilterView.as_view(), name='apply_filter'),
]
