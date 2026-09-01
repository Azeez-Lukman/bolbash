from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import sitemaps
from core import views as core_views

urlpatterns = [
    path('robots.txt', core_views.robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('admin/', admin.site.urls),
    path('booking/', include('booking.urls')),
    path('payments/', include('payments.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('academy/', include('academy.urls', namespace='academy')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('shop/', include('shop.urls', namespace='shop')),
    path('admin-portal/', include('admin_panel.urls', namespace='admin_panel')),
    path('', include('core.urls')),
]

handler404 = 'core.views.custom_404'
handler403 = 'core.views.custom_403'
handler500 = 'core.views.custom_500'


from django.urls import re_path
from django.views.static import serve

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Serve media files on cloud hosts (e.g. Render)
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]


