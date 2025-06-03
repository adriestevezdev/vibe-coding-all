-- Add generated_at field to prompts table
ALTER TABLE prompts ADD COLUMN IF NOT EXISTS generated_at TIMESTAMP WITH TIME ZONE;

-- Create index on generated_at for better query performance
CREATE INDEX IF NOT EXISTS idx_prompts_generated_at ON prompts(generated_at);

-- Update existing prompts with generated_content to have generated_at timestamp
UPDATE prompts 
SET generated_at = updated_at 
WHERE generated_content IS NOT NULL 
  AND generated_at IS NULL;
