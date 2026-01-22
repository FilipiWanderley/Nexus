-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Profiles Table (Extends Supabase auth.users)
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    linkedin_url TEXT,
    portfolio_url TEXT,
    target_role TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Resumes Table
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    parsed_content JSONB DEFAULT '{}'::JSONB,
    raw_text TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Job Descriptions Table (Kanban Board Core)
CREATE TYPE job_status AS ENUM ('saved', 'applied', 'interviewing', 'offer', 'rejected');

CREATE TABLE job_descriptions (
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

-- 4. Analyses Table (The Intersection of Resume & Job)
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    job_description_id UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    match_score INTEGER CHECK (match_score >= 0 AND match_score <= 100),
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 5. Keyword Gaps Table
CREATE TYPE keyword_importance AS ENUM ('critical', 'high', 'medium', 'low');
CREATE TYPE keyword_status AS ENUM ('missing', 'partial', 'present');

CREATE TABLE keyword_gaps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    keyword TEXT NOT NULL,
    category TEXT,
    importance keyword_importance DEFAULT 'medium',
    status keyword_status DEFAULT 'missing'
);

-- 6. Rewrite Suggestions Table
CREATE TABLE rewrite_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    section TEXT NOT NULL,
    original_text TEXT,
    suggested_text TEXT,
    reasoning TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Row Level Security (RLS) Policies

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE keyword_gaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE rewrite_suggestions ENABLE ROW LEVEL SECURITY;

-- Profiles: Users can view and update their own profile
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Resumes: Users can CRUD their own resumes
CREATE POLICY "Users can all own resumes" ON resumes
    FOR ALL USING (auth.uid() = user_id);

-- Job Descriptions: Users can CRUD their own jobs
CREATE POLICY "Users can all own job descriptions" ON job_descriptions
    FOR ALL USING (auth.uid() = user_id);

-- Analyses: Users can CRUD their own analyses
CREATE POLICY "Users can all own analyses" ON analyses
    FOR ALL USING (auth.uid() = user_id);

-- Keyword Gaps: Access via Analysis ownership
CREATE POLICY "Users can view keyword gaps for own analyses" ON keyword_gaps
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM analyses 
            WHERE analyses.id = keyword_gaps.analysis_id 
            AND analyses.user_id = auth.uid()
        )
    );

-- Rewrite Suggestions: Access via Analysis ownership
CREATE POLICY "Users can view suggestions for own analyses" ON rewrite_suggestions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM analyses 
            WHERE analyses.id = rewrite_suggestions.analysis_id 
            AND analyses.user_id = auth.uid()
        )
    );

-- Trigger to create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name)
  VALUES (new.id, new.raw_user_meta_data->>'full_name');
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
