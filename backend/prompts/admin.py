"""
Django admin configuration for Echo models.
"""

from django.contrib import admin
from .models import Template, Prompt, EnhancedPrompt, SavedPrompt


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    """Admin interface for prompt templates."""
    list_display = ['name', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    """Admin interface for prompts."""
    list_display = ['user', 'original_text', 'template', 'created_at']
    list_filter = ['created_at', 'template__category']
    search_fields = ['original_text', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Prompt Content', {
            'fields': ('user', 'original_text', 'template')
        }),
        ('Settings', {
            'fields': ('temperature', 'max_tokens')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EnhancedPrompt)
class EnhancedPromptAdmin(admin.ModelAdmin):
    """Admin interface for enhanced prompts."""
    list_display = ['id', 'prompt', 'model_used', 'tokens_used', 'created_at']
    list_filter = ['model_used', 'created_at']
    search_fields = ['prompt__original_text', 'consolidated_prompt']
    readonly_fields = ['prompt', 'created_at', 'persona', 'task', 'context', 'format']


@admin.register(SavedPrompt)
class SavedPromptAdmin(admin.ModelAdmin):
    """Admin interface for saved prompts."""
    list_display = ['user', 'custom_title', 'category', 'is_favorite', 'created_at']
    list_filter = ['is_favorite', 'category', 'created_at']
    search_fields = ['custom_title', 'user__username', 'notes']
    fieldsets = (
        ('User & Prompts', {
            'fields': ('user', 'prompt', 'enhanced')
        }),
        ('Details', {
            'fields': ('custom_title', 'notes', 'category', 'is_favorite')
        }),
        ('Metadata', {
            'fields': ('created_at', 'last_accessed'),
            'classes': ('collapse',)
        }),
    )
