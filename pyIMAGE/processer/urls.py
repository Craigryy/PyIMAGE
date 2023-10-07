from django.urls import path
from . import views

urlpatterns = [
    path('', views.image_list, name='image_list'),
    path('upload/', views.upload_image, name='upload_image'),
    path('edit/<int:image_id>/', views.edit_image, name='edit_image'),
    path('apply_effect/<int:image_id>/', views.apply_effect, name='apply_effect'),
]
