from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView  
from .views import custom_page_not_found, custom_server_error
from django.conf.urls import handler404, handler500
from django.views.defaults import page_not_found, server_error

handler404 = 'pillycam.views.custom_page_not_found'
handler500 = 'pillycam.views.custom_server_error'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('pillycam.urls')),
    path('accounts/', include('allauth.urls')),
    path("404/", custom_page_not_found, name='custom_page_not_found'),
    re_path(r'^.*/$', custom_page_not_found),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
   
    path("", include('allauth.urls')),
    path("__debug__/", include("debug_toolbar.urls")),

]

if not settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^media/(?P<path>.*)$',
            'django.views.static.serve', {
                'document_root': settings.MEDIA_ROOT,
            })
    )
