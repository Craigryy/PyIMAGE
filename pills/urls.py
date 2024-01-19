from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from pillycam import views
from django.conf.urls import handler404, handler500


# Custom error handlers
handler404 = 'pillycam.views.custom_404'
handler500 = 'pillycam.views.custom_500'

# Your URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pillycam.urls')),
    path('accounts/', include('allauth.urls')),
    path("__debug__/", include("debug_toolbar.urls")),  # Debug Toolbar URL
    # Other paths

    # Serve static and media files from the development server in DEBUG mode
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

