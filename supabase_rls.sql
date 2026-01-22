-- =============================================================================
-- Nexus Career AI - Advanced RLS & Security Policies
-- =============================================================================

-- 1. Performance Optimization: Index Foreign Keys
-- RLS checks often join tables. Indexes are critical for performance.
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_job_descriptions_user_id ON job_descriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_resume_id ON analyses(resume_id);
CREATE INDEX IF NOT EXISTS idx_analyses_job_id ON analyses(job_description_id);

-- These two are crucial for the nested RLS policies
CREATE INDEX IF NOT EXISTS idx_keyword_gaps_analysis_id ON keyword_gaps(analysis_id);
CREATE INDEX IF NOT EXISTS idx_rewrite_suggestions_analysis_id ON rewrite_suggestions(analysis_id);


-- 2. Reset Existing Policies (Safety First)
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Users can all own resumes" ON resumes;
DROP POLICY IF EXISTS "Users can all own job descriptions" ON job_descriptions;
DROP POLICY IF EXISTS "Users can all own analyses" ON analyses;
DROP POLICY IF EXISTS "Users can view keyword gaps for own analyses" ON keyword_gaps;
DROP POLICY IF EXISTS "Users can view suggestions for own analyses" ON rewrite_suggestions;


-- 3. Profiles Policies
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);


-- 4. Resumes Policies (Full User Control)
CREATE POLICY "Users can manage own resumes" ON resumes
    FOR ALL USING (auth.uid() = user_id);


-- 5. Job Descriptions Policies (Full User Control)
CREATE POLICY "Users can manage own job descriptions" ON job_descriptions
    FOR ALL USING (auth.uid() = user_id);


-- 6. Analyses Policies (Read-Only + Delete for Users)
-- Users can see their analysis results
CREATE POLICY "Users can view own analyses" ON analyses
    FOR SELECT USING (auth.uid() = user_id);

-- Users can delete an analysis if they want to clear it
CREATE POLICY "Users can delete own analyses" ON analyses
    FOR DELETE USING (auth.uid() = user_id);

-- NOTE: INSERT/UPDATE are strictly forbidden for authenticated users.
-- The Backend (Service Role) bypasses RLS, so it can insert/update freely.


-- 7. Keyword Gaps Policies (Strict Read-Only)
CREATE POLICY "Users can view keyword gaps for own analyses" ON keyword_gaps
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM analyses 
            WHERE analyses.id = keyword_gaps.analysis_id 
            AND analyses.user_id = auth.uid()
        )
    );


-- 8. Rewrite Suggestions Policies (Strict Read-Only)
CREATE POLICY "Users can view suggestions for own analyses" ON rewrite_suggestions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM analyses 
            WHERE analyses.id = rewrite_suggestions.analysis_id 
            AND analyses.user_id = auth.uid()
        )
    );
