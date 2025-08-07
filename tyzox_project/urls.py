from django.contrib import admin
from django.urls import path, include
from django.conf import settings          # Importar settings
from django.conf.urls.static import static  # Importar static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tyzox.urls')), 
]

# Añadir esto al final del archivo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)