/**
 * Project types for the frontend
 */

/**
 * Base Project type
 */
export interface ProjectBase {
  name: string;
  description?: string;
  idea_text?: string;
  vibe_coding_tags?: string[];
  is_public: boolean;
}

/**
 * Project type for creating a new project
 */
export interface ProjectCreate extends ProjectBase {}

/**
 * Project type for updating an existing project
 */
export interface ProjectUpdate {
  name?: string;
  description?: string;
  idea_text?: string;
  vibe_coding_tags?: string[];
  is_public?: boolean;
}

/**
 * Project type as returned from the API
 */
export interface Project extends ProjectBase {
  id: string;
  user_id: string;
  share_token?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Project type with prompts included
 */
export interface ProjectWithPrompts extends Project {
  prompts: import('./prompt').Prompt[];
}