-- Optional: Insert sample data for development
-- This file is optional and can be used to seed the database with test data

-- Insert a test user (password is 'testpassword' hashed with bcrypt)
INSERT INTO users (email, password_hash, full_name, is_active) VALUES
('test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGH7yCDdylu', 'Test User', true)
ON CONFLICT (email) DO NOTHING;

-- Get the test user ID for foreign key references
WITH test_user AS (
    SELECT id FROM users WHERE email = 'test@example.com' LIMIT 1
)
-- Insert a sample project
INSERT INTO projects (user_id, name, description, idea_text, vibe_coding_tags) 
SELECT 
    id,
    'Sample Project',
    'A sample project for testing',
    'Create a web application for task management',
    ARRAY['modern', 'minimalist', 'react']
FROM test_user
WHERE NOT EXISTS (
    SELECT 1 FROM projects WHERE name = 'Sample Project'
);

-- Note: This is optional sample data for development
-- In production, users will create their own data through the application
