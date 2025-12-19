"""
Django REST Framework serializers for API request/response handling.
"""

from rest_framework import serializers
from .models import Template, Prompt, EnhancedPrompt, SavedPrompt


class TemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for Template model - converts to/from JSON.
    """
    class Meta:
        model = Template
        fields = ['id', 'name', 'category', 'description', 'system_prompt_prefix']
        read_only_fields = ['system_prompt_prefix']


class EnhancedPromptSerializer(serializers.ModelSerializer):
    """
    Serializer for EnhancedPrompt - PTCF structure with consolidated prompt.
    """
    class Meta:
        model = EnhancedPrompt
        fields = [
            'id',
            'persona',
            'task',
            'context',
            'format',
            'consolidated_prompt',
            'improvement_summary',
            'model_used',
            'tokens_used',
        ]
        read_only_fields = fields


class PromptEnhancementRequestSerializer(serializers.Serializer):
    """
    Serializer for incoming enhancement requests from frontend.
    """
    prompt_text = serializers.CharField(
        max_length=5000,
        min_length=5,
        help_text="The weak prompt to be enhanced"
    )
    template_id = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="ID of template to apply (optional)"
    )
    temperature = serializers.FloatField(
        default=0.3,
        min_value=0.1,
        max_value=1.0,
        help_text="AI creativity level"
    )
    max_tokens = serializers.IntegerField(
        default=2048,
        min_value=256,
        max_value=4096,
        help_text="Maximum response length"
    )
    custom_system_prompt = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Override system prompt (optional)"
    )


class PromptEnhancementResponseSerializer(serializers.Serializer):
    """
    Serializer for enhancement response to send back to frontend.
    """
    id = serializers.IntegerField()
    original_text = serializers.CharField()
    enhanced = EnhancedPromptSerializer()
    created_at = serializers.DateTimeField()


class SavedPromptSerializer(serializers.ModelSerializer):
    """
    Serializer for SavedPrompt model with nested enhanced prompt data.
    """
    original_text = serializers.CharField(source='prompt.original_text', read_only=True)
    enhanced = EnhancedPromptSerializer(source='enhanced', read_only=True)

    class Meta:
        model = SavedPrompt
        fields = [
            'id',
            'custom_title',
            'category',
            'original_text',
            'enhanced',
            'is_favorite',
            'created_at',
            'last_accessed',
        ]


class SavedPromptCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating saved prompts.
    """
    prompt_id = serializers.IntegerField()

    class Meta:
        model = SavedPrompt
        fields = ['prompt_id', 'custom_title', 'notes', 'category', 'is_favorite']

    def create(self, validated_data):
        """
        Create SavedPrompt with current user and prompt/enhanced from request.
        """
        request = self.context.get('request')
        prompt_id = validated_data.pop('prompt_id')

        try:
            prompt = Prompt.objects.get(id=prompt_id, user=request.user)
            enhanced = prompt.enhanced

            saved_prompt = SavedPrompt.objects.create(
                user=request.user,
                prompt=prompt,
                enhanced=enhanced,
                **validated_data
            )
            return saved_prompt

        except Prompt.DoesNotExist:
            raise serializers.ValidationError("Prompt not found")
