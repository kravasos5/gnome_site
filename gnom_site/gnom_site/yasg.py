from django.urls import re_path, path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# настройка swagger
schema_view = get_schema_view(
    openapi.Info(
        title="GnomeSite API",
        default_version='v1',
        description="GnomeSite REST API documentation",
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# маршруты для swagger
urlpatterns = [
   path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]