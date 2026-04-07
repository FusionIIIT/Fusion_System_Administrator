-- Add is_singular column to globals_designation table
ALTER TABLE globals_designation ADD COLUMN is_singular BOOLEAN DEFAULT FALSE;

-- Update existing singular roles (examples - adjust based on your actual data)
-- UPDATE globals_designation SET is_singular = TRUE WHERE name IN ('director', 'dean', 'hod');
