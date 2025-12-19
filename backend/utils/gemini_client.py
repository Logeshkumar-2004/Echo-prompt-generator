"""
Wrapper for Google Generative AI (Gemini) API client.
Handles API calls and response parsing with error handling.
"""

import json
import logging
from typing import Dict, Any, Optional
from django.conf import settings
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Client for interacting with Gemini 2.5 Flash model.
    """

    def __init__(self):
        """Initialize Gemini with API key from Django settings."""
        self.api_key = settings.GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def enhance_prompt(
        self,
        weak_prompt: str,
        system_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """
        Transform weak prompt into strong PTCF-formatted prompt using Gemini.

        Args:
            weak_prompt: User's original weak prompt
            system_prompt: System context/persona for the model
            temperature: Creativity level (0.1 = focused, 1.0 = creative)
            max_tokens: Maximum response length

        Returns:
            Dictionary with PTCF structure and metadata
        """
        try:
            # Build complete prompt with system context
            full_prompt = f"""{system_prompt}

CRITICAL: Output ONLY valid JSON. No explanations, no markdown, no extra text.

User prompt to transform: "{weak_prompt}"

Return ONLY this exact JSON format with no other text:
{{
  "original_prompt": "{weak_prompt}",
  "persona": {{"role": "specific role", "expertise": "area of expertise", "perspective": "unique perspective"}},
  "task": {{"objective": "clear objective", "deliverable": "expected output", "constraints": ["constraint1", "constraint2"]}},
  "context": {{"technical_background": "relevant background", "key_considerations": ["consideration1"], "audience": "target audience"}},
  "format": {{"output_style": "style description", "structure": ["element1", "element2"], "tone": "tone"}},
  "consolidated_prompt": "the final enhanced prompt text here",
  "improvement_summary": "brief explanation of improvements"
}}"""

            # Call Gemini API
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    top_p=0.9,
                    top_k=40,
                ),
            )

            # Extract response text
            response_text = response.text

            # Parse JSON from response
            parsed_response = self._extract_json(response_text)

            # Log success
            logger.info(f"Successfully enhanced prompt with {len(parsed_response)} fields")

            return {
                'success': True,
                'data': parsed_response,
                'tokens_used': response.usage_metadata.output_tokens,
                'model': 'gemini-2.5-flash',
            }

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return {
                'success': False,
                'error': 'Failed to parse AI response as JSON',
                'details': str(e),
            }
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {
                'success': False,
                'error': 'Failed to enhance prompt',
                'details': str(e),
            }

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from response text using boundary detection.
        More reliable than regex for nested structures.

        Args:
            text: Response text that may contain JSON and extra text

        Returns:
            Parsed JSON dictionary
        """
        # Find first { and last }
        start_idx = text.find('{')
        end_idx = text.rfind('}')

        if start_idx == -1 or end_idx == -1:
            raise json.JSONDecodeError("No JSON structure found", text, 0)

        # Extract JSON substring and parse
        json_str = text[start_idx : end_idx + 1]
        return json.loads(json_str)
