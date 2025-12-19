"""
Database models for Echo prompt enhancement application.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator


class Template(models.Model):
    """
    Pre-configured prompt templates for different use cases.
    """
    CATEGORY_CHOICES = [
        ('code', 'Code'),
        ('content', 'Content'),
        ('data', 'Data'),
        ('creative', 'Creative'),
        ('business', 'Business'),
        ('research', 'Research'),
    ]

    id = models.CharField(max_length=50, primary_key=True)  # e.g., 'code-gen'
    name = models.CharField(max_length=100)  # e.g., 'Code Generation'
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()  # Brief description of template purpose
    system_prompt_prefix = models.TextField()  # System prompt override for this template
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.category})"


class Prompt(models.Model):
    """
    Original weak prompt submitted by user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    original_text = models.TextField(validators=[MinLengthValidator(5)])  # At least 5 characters
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Enhancement metadata
    temperature = models.FloatField(default=0.3)  # Gemini temperature setting
    max_tokens = models.IntegerField(default=2048)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return self.original_text[:50] + "..."


class EnhancedPrompt(models.Model):
    """
    AI-generated enhanced prompt with PTCF structure.
    One-to-one relationship with Prompt (each prompt enhancement produces one result).
    """
    prompt = models.OneToOneField(Prompt, on_delete=models.CASCADE, related_name='enhanced')

    # PTCF Components (JSON structure)
    persona = models.JSONField()  # {"role": str, "expertise": str, "perspective": str}
    task = models.JSONField()  # {"objective": str, "deliverable": str, "constraints": list}
    context = models.JSONField()  # {"technical_background": str, "key_considerations": list, "audience": str}
    format = models.JSONField()  # {"output_style": str, "structure": list, "tone": str}

    # Final consolidated prompt
    consolidated_prompt = models.TextField()  # Full, production-ready prompt
    improvement_summary = models.TextField()  # Brief explanation of improvements made

    # API response metadata
    model_used = models.CharField(max_length=50, default='gemini-2.5-flash')
    tokens_used = models.IntegerField(null=True, blank=True)
    processing_time_ms = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Enhanced: {self.prompt.original_text[:30]}..."


class SavedPrompt(models.Model):
    """
    User-saved prompt pairs for later reference/reuse.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_prompts')
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    enhanced = models.ForeignKey(EnhancedPrompt, on_delete=models.CASCADE)

    # User metadata
    custom_title = models.CharField(max_length=200, null=True, blank=True)
    notes = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True)

    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_accessed']
        unique_together = ['user', 'prompt', 'enhanced']
        indexes = [
            models.Index(fields=['user', '-last_accessed']),
            models.Index(fields=['user', 'is_favorite']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.custom_title or 'Untitled'}"
