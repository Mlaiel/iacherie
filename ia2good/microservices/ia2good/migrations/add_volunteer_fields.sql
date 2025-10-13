-- Migration: Add missing fields to ia2good_volunteer_profiles
-- Date: 2025-10-08
-- Description: Add full_name, phone, email, bio, profile_photo and compatibility aliases

BEGIN;

-- Add personal information fields
ALTER TABLE ia2good_volunteer_profiles 
ADD COLUMN IF NOT EXISTS full_name VARCHAR(200),
ADD COLUMN IF NOT EXISTS phone VARCHAR(20),
ADD COLUMN IF NOT EXISTS email VARCHAR(255),
ADD COLUMN IF NOT EXISTS bio TEXT,
ADD COLUMN IF NOT EXISTS profile_photo VARCHAR(500);

-- Add compatibility aliases for is_available
ALTER TABLE ia2good_volunteer_profiles 
ADD COLUMN IF NOT EXISTS is_available BOOLEAN DEFAULT TRUE;

-- Add compatibility aliases for availability_hours
ALTER TABLE ia2good_volunteer_profiles 
ADD COLUMN IF NOT EXISTS availability_hours JSONB DEFAULT '{}'::jsonb;

-- Add compatibility aliases for verification
ALTER TABLE ia2good_volunteer_profiles 
ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS verification_level VARCHAR(20) DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS verification_notes TEXT;

-- Add compatibility aliases for statistics
ALTER TABLE ia2good_volunteer_profiles 
ADD COLUMN IF NOT EXISTS cases_completed INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_hours INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS rating FLOAT DEFAULT 0.0;

-- Update existing records to sync alias fields with main fields
UPDATE ia2good_volunteer_profiles SET
    is_available = availability_status,
    availability_hours = availability_schedule,
    is_verified = (verification_status = 'verified'),
    verification_level = verification_status,
    cases_completed = total_cases_completed,
    total_hours = total_hours_volunteered,
    rating = COALESCE(average_rating, 0.0)
WHERE full_name IS NULL;

-- Add NOT NULL constraint to critical fields after population
-- ALTER TABLE ia2good_volunteer_profiles ALTER COLUMN full_name SET NOT NULL;
-- ALTER TABLE ia2good_volunteer_profiles ALTER COLUMN email SET NOT NULL;

-- Create indexes for new fields
CREATE INDEX IF NOT EXISTS idx_ia2good_volunteers_email ON ia2good_volunteer_profiles(email);
CREATE INDEX IF NOT EXISTS idx_ia2good_volunteers_is_verified ON ia2good_volunteer_profiles(is_verified);
CREATE INDEX IF NOT EXISTS idx_ia2good_volunteers_is_available ON ia2good_volunteer_profiles(is_available);

COMMIT;
