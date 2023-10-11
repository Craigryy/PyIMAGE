from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout

from processer.views import (Home, ImageProcessing,
                        DeleteImage, SaveProcessedImage, Effects)


from . import views
 
# urlpatterns = [    
#   path(r'^$', Home.as_view(), name='home'),
#   path(r'^image/$', ImageProcessing.as_view(), name='image'),
#   path(r'^effects/', Effects.as_view(), name='effects'),
#   path(r'^accounts/logout/$', logout,
#       {'next_page': '/accounts/login/'}, name="logout"),
#   path(r'^image/(?P<id>[0-9]+)/delete/$',
#         DeleteImage.as_view(), name='delete'),
#   path(r'^save-effects/', SaveProcessedImage.as_view(), name='save_effects'),
# ]

urlpatterns = []