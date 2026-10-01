from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from APP.views import health


urlpatterns = [
    path('admin/', admin.site.urls),
    path("health"),
    path("", include("APP.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
