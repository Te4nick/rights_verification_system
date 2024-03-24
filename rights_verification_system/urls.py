"""
URL configuration for rights_verification_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from access.views import AccessViewSet

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path(
        "access",
        AccessViewSet.as_view(
            {
                "post": "post_access",
                "get": "get_access",
            }
        ),
        name="access_ops",
    ),
    path(
        "access/forbidden",
        AccessViewSet.as_view(
            {
                "get": "get_forbidden",
            }
        ),
        name="forbidden_ops",
    ),
    path(
        "log/",
        AccessViewSet.as_view(
            {
                "get": "get_log_file",
            }
        ),
        name="get_log_file",
    ),
    path(
        "log/status/",
        AccessViewSet.as_view(
            {
                "get": "get_log_file_status",
            }
        ),
        name="get_log_file_status",
    ),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
