from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from business_hub import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/live", views.live, name="health-live"),
    path("health/ready", views.ready, name="health-ready"),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="api-schema"), name="redoc"),
    path("api-docs", SpectacularSwaggerView.as_view(url_name="api-schema"), name="swagger-ui-alias"),
    path("api-redoc", SpectacularRedocView.as_view(url_name="api-schema"), name="redoc-alias"),
    path("api/v1/business-hub/", include("business_hub.urls")),
]
