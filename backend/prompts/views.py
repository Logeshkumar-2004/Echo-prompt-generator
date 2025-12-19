"""
Django REST Framework views for Echo API endpoints.
Handles prompt enhancement, templates, and saved prompts.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.utils.timezone import now
import time
import logging

from .models import Template, Prompt, EnhancedPrompt, SavedPrompt
from .serializers import (
    TemplateSerializer,
    PromptEnhancementRequestSerializer,
    PromptEnhancementResponseSerializer,
    SavedPromptSerializer,
    SavedPromptCreateSerializer,
)
from utils.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for templates.
    GET /api/templates/ - List all templates
    GET /api/templates/{id}/ - Retrieve single template
    """
    queryset = Template.objects.filter(is_active=True)
    serializer_class = TemplateSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['category']
    search_fields = ['name', 'category']


class PromptEnhancementViewSet(viewsets.ModelViewSet):
    """
    API endpoint for prompt enhancement.
    POST /api/prompts/enhance/ - Enhance a weak prompt
    GET /api/prompts/{id}/ - Get enhancement result
    """
    serializer_class = PromptEnhancementResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    def get_queryset(self):
        """Return only prompts owned by current user."""
        return Prompt.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def enhance(self, request):
        """
        POST endpoint to enhance a weak prompt.
        
        Request body:
        {
            "prompt_text": "weak prompt here",
            "template_id": "code-gen" (optional),
            "temperature": 0.3,
            "max_tokens": 2048,
            "custom_system_prompt": "override" (optional)
        }
        
        Returns enhanced prompt with PTCF structure.
        """
        # Validate request
        serializer = PromptEnhancementRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        prompt_text = data['prompt_text']
        template_id = data.get('template_id')
        temperature = data.get('temperature', 0.3)
        max_tokens = data.get('max_tokens', 2048)
        custom_system_prompt = data.get('custom_system_prompt', '')

        # Get template if provided
        template = None
        system_prompt = 'You are a prompt engineer specializing in PTCF framework optimization.'
        
        if template_id:
            try:
                template = Template.objects.get(id=template_id)
                system_prompt = template.system_prompt_prefix
            except Template.DoesNotExist:
                return Response(
                    {'error': 'Template not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Override system prompt if custom one provided
        if custom_system_prompt:
            system_prompt = custom_system_prompt

        # Create Prompt record
        prompt = Prompt.objects.create(
            user=request.user,
            original_text=prompt_text,
            template=template,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Call Gemini API
        start_time = time.time()
        client = GeminiClient()
        result = client.enhance_prompt(
            weak_prompt=prompt_text,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Handle API errors
        if not result['success']:
            return Response(
                {'error': result['error'], 'details': result.get('details')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parse and store enhanced prompt
        try:
            enhanced_data = result['data']
            enhanced = EnhancedPrompt.objects.create(
                prompt=prompt,
                persona=enhanced_data['persona'],
                task=enhanced_data['task'],
                context=enhanced_data['context'],
                format=enhanced_data['format'],
                consolidated_prompt=enhanced_data['consolidated_prompt'],
                improvement_summary=enhanced_data['improvement_summary'],
                model_used=result['model'],
                tokens_used=result.get('tokens_used'),
                processing_time_ms=processing_time_ms,
            )

            # Return response with enhanced prompt
            response_serializer = PromptEnhancementResponseSerializer(prompt)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except KeyError as e:
            logger.error(f"Missing field in Gemini response: {e}")
            return Response(
                {'error': f'Invalid response structure: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        GET endpoint to retrieve user's prompt history.
        Supports filtering by date and pagination.
        """
        queryset = self.get_queryset()
        
        # Optional date filtering
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SavedPromptViewSet(viewsets.ModelViewSet):
    """
    API endpoint for saved prompts.
    GET /api/saved/ - List user's saved prompts
    POST /api/saved/ - Save a prompt
    DELETE /api/saved/{id}/ - Delete saved prompt
    PATCH /api/saved/{id}/ - Update saved prompt
    """
    serializer_class = SavedPromptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only saved prompts owned by current user."""
        return SavedPrompt.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a new saved prompt."""
        serializer = SavedPromptCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return full saved prompt data
        saved = serializer.instance
        return_serializer = SavedPromptSerializer(saved)
        return Response(return_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def favorites(self, request):
        """Get all favorite saved prompts."""
        favorites = self.get_queryset().filter(is_favorite=True)
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle favorite status of saved prompt."""
        saved_prompt = self.get_object()
        saved_prompt.is_favorite = not saved_prompt.is_favorite
        saved_prompt.save()
        
        serializer = self.get_serializer(saved_prompt)
        return Response(serializer.data)
