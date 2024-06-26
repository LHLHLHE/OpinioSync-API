from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from . import settings

admin.site.site_header = 'Администрирование OpinioSync'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls'))
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
