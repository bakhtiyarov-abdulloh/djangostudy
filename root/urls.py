from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from root import settings
from root.settings import MEDIA_ROOT, MEDIA_URL

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include('apps.urls')),
                  path("ckeditor5/", include('django_ckeditor_5.urls')),

              ] + static(MEDIA_URL, document_root=MEDIA_ROOT) + static(settings.MEDIA_URL,
                                                                       document_root=settings.MEDIA_ROOT)
