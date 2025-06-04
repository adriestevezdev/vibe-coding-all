-- Add is_premium field to users table for Polar payment integration
-- Migration: 005_add_is_premium_to_users.sql

-- Add is_premium column to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_premium BOOLEAN DEFAULT false;

-- Add index for performance since we'll query on this field
CREATE INDEX IF NOT EXISTS idx_users_is_premium ON users(is_premium);

-- Add comment for documentation
COMMENT ON COLUMN users.is_premium IS 'Indicates if user has active premium subscription via Polar.sh';

-- Update existing users to have is_premium = false (default)
UPDATE users 
SET is_premium = false 
WHERE is_premium IS NULL;