-- Add share_token column to prompts table for sharing functionality
ALTER TABLE prompts ADD COLUMN share_token VARCHAR(255) NULL;

-- Add unique constraint and index for share_token
CREATE UNIQUE INDEX idx_prompts_share_token ON prompts(share_token) WHERE share_token IS NOT NULL;