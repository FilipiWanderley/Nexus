
-- =============================================================================
-- NEXUS CAREER AI - FULL DATABASE SETUP SCRIPT
-- =============================================================================
-- INSTRUCTIONS:
-- 1. Copy this entire script.
-- 2. Go to your Supabase Dashboard -> SQL Editor.
-- 3. Paste and Run.
-- =============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 1. TABLES & SCHEMA
-- =============================================================================

-- Profiles Table (Extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    linkedin_url TEXT,
    portfolio_url TEXT,
    target_role TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Resumes Table
CREATE TABLE IF NOT EXISTS resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    parsed_content JSONB DEFAULT '{}'::JSONB,
    raw_text TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Job Descriptions Table
DROP TYPE IF EXISTS job_status CASCADE;
CREATE TYPE job_status AS ENUM ('saved', 'applied', 'interviewing', 'offer', 'rejected');

CREATE TABLE IF NOT EXISTS job_descriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    url TEXT,
    raw_text TEXT,
    status job_status DEFAULT 'saved',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Analyses Table
CREATE TABLE IF NOT EXISTS analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES resumes(id) ON DELETE CASCADE, -- Made nullable temporarily just in case
    job_description_id UUID REFERENCES job_descriptions(id) ON DELETE CASCADE, -- Made nullable
    match_score INTEGER CHECK (match_score >= 0 AND match_score <= 100),
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Keyword Gaps Table
DROP TYPE IF EXISTS keyword_importance CASCADE;
DROP TYPE IF EXISTS keyword_status CASCADE;
CREATE TYPE keyword_importance AS ENUM ('critical', 'high', 'medium', 'low');
CREATE TYPE keyword_status AS ENUM ('missing', 'partial', 'present');

CREATE TABLE IF NOT EXISTS keyword_gaps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    keyword TEXT NOT NULL,
    category TEXT,
    importance keyword_importance DEFAULT 'medium',
    status keyword_status DEFAULT 'missing'
);

-- Rewrite Suggestions Table
CREATE TABLE IF NOT EXISTS rewrite_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    section TEXT NOT NULL,
    original_text TEXT,
    suggested_text TEXT,
    reasoning TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- =============================================================================
-- 2. ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================================================

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE keyword_gaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE rewrite_suggestions ENABLE ROW LEVEL SECURITY;

-- Clear old policies to avoid conflicts
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Users can all own resumes" ON resumes;
DROP POLICY IF EXISTS "Users can all own job descriptions" ON job_descriptions;
DROP POLICY IF EXISTS "Users can all own analyses" ON analyses;
DROP POLICY IF EXISTS "Users can view keyword gaps for own analyses" ON keyword_gaps;
DROP POLICY IF EXISTS "Users can view suggestions for own analyses" ON rewrite_suggestions;

-- Define Policies

-- Profiles
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Resumes
CREATE POLICY "Users can all own resumes" ON resumes
    FOR ALL USING (auth.uid() = user_id);

-- Job Descriptions
CREATE POLICY "Users can all own job descriptions" ON job_descriptions
    FOR ALL USING (auth.uid() = user_id);

-- Analyses
CREATE POLICY "Users can all own analyses" ON analyses
    FOR ALL USING (auth.uid() = user_id);

-- Keyword Gaps
CREATE POLICY "Users can view keyword gaps for own analyses" ON keyword_gaps
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM analyses 
            WHERE analyses.id = keyword_gaps.analysis_id 
            AND analyses.user_id = auth.uid()
        )
    );

-- Rewrite Suggestions
CREATE POLICY "Users can view suggestions for own analyses" ON rewrite_suggestions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM analyses 
            WHERE analyses.id = rewrite_suggestions.analysis_id 
            AND analyses.user_id = auth.uid()
        )
    );

-- =============================================================================
-- 3. TRIGGERS (Auto Profile Creation)
-- =============================================================================

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name)
  VALUES (new.id, new.raw_user_meta_data->>'full_name')
  ON CONFLICT (id) DO NOTHING;
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- =============================================================================
-- 4. STORAGE BUCKETS & POLICIES
-- =============================================================================

-- Bucket: resumes
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'resumes', 
  'resumes', 
  false, 
  5242880, 
  ARRAY['application/pdf']
)
ON CONFLICT (id) DO UPDATE SET 
  public = false,
  file_size_limit = 5242880,
  allowed_mime_types = ARRAY['application/pdf'];

-- Storage Policies
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can upload their own resumes" ON storage.objects;
DROP POLICY IF EXISTS "Users can view their own resumes" ON storage.objects;
DROP POLICY IF EXISTS "Users can update their own resumes" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete their own resumes" ON storage.objects;

-- Insert
CREATE POLICY "Users can upload their own resumes"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'resumes' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Select
CREATE POLICY "Users can view their own resumes"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'resumes' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Update
CREATE POLICY "Users can update their own resumes"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'resumes' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Delete
CREATE POLICY "Users can delete their own resumes"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'resumes' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

