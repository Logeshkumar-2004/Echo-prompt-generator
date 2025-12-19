import apiClient from './api';

export interface EnhancePromptRequest {
  prompt_text: string;
  template_id?: string;
  temperature?: number;
  max_tokens?: number;
  custom_system_prompt?: string;
}

export interface EnhancedPromptResponse {
  id: number;
  original_text: string;
  enhanced: {
    id: number;
    persona: {
      role: string;
      expertise: string;
      perspective: string;
    };
    task: {
      objective: string;
      deliverable: string;
      constraints: string[];
    };
    context: {
      technical_background: string;
      key_considerations: string[];
      audience: string;
    };
    format: {
      output_style: string;
      structure: string[];
      tone: string;
    };
    consolidated_prompt: string;
    improvement_summary: string;
    model_used: string;
    tokens_used: number;
  };
  created_at: string;
}

/**
 * Send weak prompt to Django backend for enhancement
 * Backend calls Gemini API and returns PTCF-structured result
 */
export const enhancePrompt = async (
  request: EnhancePromptRequest
): Promise<EnhancedPromptResponse> => {
  const response = await apiClient.post('/prompts/enhance/', request);
  return response.data;
};

/**
 * Fetch user's prompt enhancement history
 */
export const getPromptHistory = async (page = 1) => {
  const response = await apiClient.get('/prompts/history/', {
    params: { page },
  });
  return response.data;
};

/**
 * Get single prompt with its enhancement
 */
export const getPrompt = async (promptId: number): Promise<EnhancedPromptResponse> => {
  const response = await apiClient.get(`/prompts/${promptId}/`);
  return response.data;
};
