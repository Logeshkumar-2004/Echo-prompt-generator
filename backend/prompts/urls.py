"""
URL routing for Echo API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TemplateViewSet, PromptEnhancementViewSet, SavedPromptViewSet

# Create router for ViewSets (automatic URL patterns)
router = DefaultRouter()
router.register(r'templates', TemplateViewSet, basename='template')
router.register(r'prompts', PromptEnhancementViewSet, basename='prompt')
router.register(r'saved', SavedPromptViewSet, basename='saved-prompt')

# Include router URLs
urlpatterns = [
    path('', include(router.urls)),
]
