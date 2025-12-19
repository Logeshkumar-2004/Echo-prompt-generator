"""
Main URL routing for Django project.
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),

    # API Routes
    path('api/', include('prompts.urls')),

    # Auth (if using Django auth)
    path('api-auth/', include('rest_framework.urls')),
]
