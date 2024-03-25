from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import (
  SpectacularAPIView,
  SpectacularSwaggerView,
  SpectacularRedocView
)

urlpatterns = [
  path('admin/', admin.site.urls),
  path("__debug__/", include("debug_toolbar.urls")),
  path("api/service/", include("service.urls", namespace="service")),
  path("api/user/", include("user.urls", namespace="user")),
  path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
  # Optional UI:
  path(
    'api/doc/swagger/',
    SpectacularSwaggerView.as_view(url_name='schema'),
    name='swagger-ui'
  ),
  path(
    'api/doc/redoc/',
    SpectacularRedocView.as_view(url_name='schema'),
    name='redoc'
  ),] + static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
