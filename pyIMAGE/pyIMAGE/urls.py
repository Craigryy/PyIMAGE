from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from allauth.account.views import SignupView

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('processer.urls')),
    path('accounts/', include('allauth.urls')),
]


# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
