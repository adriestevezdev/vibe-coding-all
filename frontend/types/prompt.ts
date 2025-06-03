/**
 * Base prompt interface
 */
export interface PromptBase {
  prompt_text: string;
  prompt_type?: string;
}

/**
 * Prompt creation interface
 */
export interface PromptCreate extends PromptBase {
  project_id: string;
}

/**
 * Prompt update interface
 */
export interface PromptUpdate {
  prompt_text?: string;
  generated_content?: string;
  prompt_type?: string;
  status?: string;
}

/**
 * Prompt interface as returned from API
 */
export interface Prompt extends PromptBase {
  id: string;
  project_id: string;
  user_id: string;
  generated_content?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

/**
 * Prompt with versions
 */
export interface PromptWithVersions extends Prompt {
  versions: PromptVersion[];
}

/**
 * Prompt version interface
 */
export interface PromptVersion {
  id: string;
  prompt_id: string;
  version_number: number;
  content: string;
  created_at: string;
}