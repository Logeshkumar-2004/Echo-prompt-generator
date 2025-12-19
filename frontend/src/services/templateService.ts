import apiClient from './api';

export interface Template {
  id: string;
  name: string;
  category: string;
  description: string;
  system_prompt_prefix: string;
}

/**
 * Fetch all available prompt templates from Django backend
 */
export const getTemplates = async (): Promise<Template[]> => {
  const response = await apiClient.get('/templates/');
  return response.data.results || response.data;
};

/**
 * Get templates filtered by category
 */
export const getTemplatesByCategory = async (category: string): Promise<Template[]> => {
  const response = await apiClient.get('/templates/', {
    params: { category },
  });
  return response.data.results || response.data;
};

/**
 * Get single template by ID
 */
export const getTemplate = async (templateId: string): Promise<Template> => {
  const response = await apiClient.get(`/templates/${templateId}/`);
  return response.data;
};
