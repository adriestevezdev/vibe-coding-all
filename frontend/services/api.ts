/**
 * API service for interacting with the backend
 */
import { Project, ProjectCreate, ProjectUpdate } from '../types/project';
import { Prompt, PromptCreate, PromptUpdate } from '../types/prompt';

/**
 * PromptVersion interface
 */
export interface PromptVersion {
  id: string;
  version_number: number;
  prompt_text: string;
  generated_content: string | null;
  created_at: string;
}

// Base API URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

/**
 * Get the authentication token from local storage
 */
const getToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token');
  }
  return null;
};

/**
 * Create headers with authentication token
 */
const createHeaders = (): HeadersInit => {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

/**
 * Handle API response
 */
const handleResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: 'An unknown error occurred',
    }));
    throw new Error(error.message || `Error ${response.status}`);
  }
  return response.json();
};

/**
 * Project API functions
 */
export const projectApi = {
  /**
   * Get all projects for the current user
   */
  getProjects: async (): Promise<Project[]> => {
    const response = await fetch(`${API_URL}/projects/`, {
      headers: createHeaders(),
    });
    return handleResponse<Project[]>(response);
  },

  /**
   * Get a project by ID
   */
  getProject: async (id: string): Promise<Project> => {
    const response = await fetch(`${API_URL}/projects/${id}`, {
      headers: createHeaders(),
    });
    return handleResponse<Project>(response);
  },

  /**
   * Create a new project
   */
  createProject: async (project: ProjectCreate): Promise<Project> => {
    const response = await fetch(`${API_URL}/projects/`, {
      method: 'POST',
      headers: createHeaders(),
      body: JSON.stringify(project),
    });
    return handleResponse<Project>(response);
  },

  /**
   * Update a project
   */
  updateProject: async (id: string, project: ProjectUpdate): Promise<Project> => {
    const response = await fetch(`${API_URL}/projects/${id}`, {
      method: 'PUT',
      headers: createHeaders(),
      body: JSON.stringify(project),
    });
    return handleResponse<Project>(response);
  },

  /**
   * Delete a project
   */
  deleteProject: async (id: string): Promise<Project> => {
    const response = await fetch(`${API_URL}/projects/${id}`, {
      method: 'DELETE',
      headers: createHeaders(),
    });
    return handleResponse<Project>(response);
  },
};

/**
 * Prompt API functions
 */
export const promptApi = {
  /**
   * Get all prompts for a project
   */
  getPrompts: async (projectId: string): Promise<Prompt[]> => {
    const response = await fetch(`${API_URL}/projects/${projectId}/prompts/`, {
      headers: createHeaders(),
    });
    return handleResponse<Prompt[]>(response);
  },

  /**
   * Get a prompt by ID
   */
  getPrompt: async (projectId: string, promptId: string): Promise<Prompt> => {
    const response = await fetch(`${API_URL}/projects/${projectId}/prompts/${promptId}`, {
      headers: createHeaders(),
    });
    return handleResponse<Prompt>(response);
  },

  /**
   * Create a new prompt
   */
  createPrompt: async (projectId: string, prompt: PromptCreate): Promise<Prompt> => {
    const response = await fetch(`${API_URL}/projects/${projectId}/prompts/`, {
      method: 'POST',
      headers: createHeaders(),
      body: JSON.stringify({ ...prompt, project_id: projectId }),
    });
    return handleResponse<Prompt>(response);
  },

  /**
   * Update a prompt
   */
  updatePrompt: async (projectId: string, promptId: string, prompt: PromptUpdate): Promise<Prompt> => {
    const response = await fetch(`${API_URL}/projects/${projectId}/prompts/${promptId}`, {
      method: 'PUT',
      headers: createHeaders(),
      body: JSON.stringify(prompt),
    });
    return handleResponse<Prompt>(response);
  },

  /**
   * Delete a prompt
   */
  deletePrompt: async (projectId: string, promptId: string): Promise<Prompt> => {
    const response = await fetch(`${API_URL}/projects/${projectId}/prompts/${promptId}`, {
      method: 'DELETE',
      headers: createHeaders(),
    });
    return handleResponse<Prompt>(response);
  },

  /**
   * Create a share link for a prompt
   */
  createShareLink: async (promptId: string): Promise<{share_token: string, share_url: string}> => {
    const response = await fetch(`${API_URL}/prompts/${promptId}/share`, {
      method: 'POST',
      headers: createHeaders(),
    });
    return handleResponse<{share_token: string, share_url: string}>(response);
  },

  /**
   * Get a shared prompt by token (public access)
   */
  getSharedPrompt: async (token: string): Promise<Prompt> => {
    const response = await fetch(`${API_URL}/share/${token}`);
    return handleResponse<Prompt>(response);
  },

  /**
   * Get all versions of a prompt
   */
  getPromptVersions: async (projectId: string, promptId: string): Promise<PromptVersion[]> => {
    const response = await fetch(`${API_URL}/projects/${projectId}/prompts/${promptId}/versions`, {
      headers: createHeaders(),
    });
    return handleResponse<PromptVersion[]>(response);
  },

  /**
   * Get a specific version of a prompt
   */
  getPromptVersion: async (projectId: string, promptId: string, versionNumber: number): Promise<PromptVersion> => {
    const response = await fetch(`${API_URL}/projects/${projectId}/prompts/${promptId}/versions/${versionNumber}`, {
      headers: createHeaders(),
    });
    return handleResponse<PromptVersion>(response);
  },

  /**
   * Restore a prompt to a specific version
   */
  restorePromptVersion: async (projectId: string, promptId: string, versionNumber: number): Promise<Prompt> => {
    const response = await fetch(`${API_URL}/projects/${projectId}/prompts/${promptId}/versions/${versionNumber}/restore`, {
      method: 'POST',
      headers: createHeaders(),
    });
    return handleResponse<Prompt>(response);
  },
};

/**
 * Payment API types
 */
export interface CheckoutRequest {
  product_id: string;
  success_url?: string;
  metadata?: Record<string, any>;
}

export interface CheckoutResponse {
  checkout_id: string;
  checkout_url: string;
  status: string;
}

export interface UserPremiumStatus {
  user_id: string;
  email: string;
  is_premium: boolean;
  premium_features: {
    unlimited_prompts: boolean;
    advanced_exports: boolean;
    priority_support: boolean;
  };
}

export interface Product {
  id: string;
  name: string;
  description: string;
  price: string;
  currency: string;
  interval: string;
  features: string[];
}

export interface ProductsResponse {
  products: Product[];
}

/**
 * Payment API functions
 */
export const paymentApi = {
  /**
   * Create a checkout session
   */
  createCheckoutSession: async (request: CheckoutRequest): Promise<CheckoutResponse> => {
    const response = await fetch(`${API_URL}/payments/create-checkout-session`, {
      method: 'POST',
      headers: createHeaders(),
      body: JSON.stringify(request),
    });
    return handleResponse<CheckoutResponse>(response);
  },

  /**
   * Get checkout details
   */
  getCheckoutDetails: async (checkoutId: string): Promise<any> => {
    const response = await fetch(`${API_URL}/payments/checkout/${checkoutId}`, {
      headers: createHeaders(),
    });
    return handleResponse<any>(response);
  },

  /**
   * Get user premium status
   */
  getUserPremiumStatus: async (): Promise<UserPremiumStatus> => {
    const response = await fetch(`${API_URL}/payments/user/premium-status`, {
      headers: createHeaders(),
    });
    return handleResponse<UserPremiumStatus>(response);
  },

  /**
   * Get available products
   */
  getProducts: async (): Promise<ProductsResponse> => {
    const response = await fetch(`${API_URL}/payments/products`, {
      headers: createHeaders(),
    });
    return handleResponse<ProductsResponse>(response);
  },
};

/**
 * Combined API service
 */
const api = {
  projects: projectApi,
  prompts: promptApi,
  payments: paymentApi,
};

export default api;