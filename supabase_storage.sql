-- Enable the storage extension if not already enabled (usually enabled by default in Supabase)
-- create extension if not exists "storage";

-- 1. Create the 'resumes' bucket
-- We use INSERT into storage.buckets
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'resumes', 
  'resumes', 
  false, -- Private bucket
  5242880, -- 5MB limit (5 * 1024 * 1024)
  ARRAY['application/pdf']
)
on conflict (id) do update set 
  public = false,
  file_size_limit = 5242880,
  allowed_mime_types = ARRAY['application/pdf'];

-- 2. Enable RLS on objects (just in case)
alter table storage.objects enable row level security;

-- 3. Drop existing policies to avoid conflicts
drop policy if exists "Users can upload their own resumes" on storage.objects;
drop policy if exists "Users can view their own resumes" on storage.objects;
drop policy if exists "Users can update their own resumes" on storage.objects;
drop policy if exists "Users can delete their own resumes" on storage.objects;

-- 4. Define Policies
-- We enforce a folder structure: user_id/filename.pdf
-- The helper function storage.foldername(name) returns an array of path parts.

-- Policy: INSERT
-- Allow upload if:
-- 1. User is authenticated
-- 2. Bucket is 'resumes'
-- 3. The first folder in the path matches the user's ID
create policy "Users can upload their own resumes"
on storage.objects for insert
to authenticated
with check (
  bucket_id = 'resumes' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy: SELECT
-- Allow read if:
-- 1. User is authenticated
-- 2. Bucket is 'resumes'
-- 3. The first folder in the path matches the user's ID
create policy "Users can view their own resumes"
on storage.objects for select
to authenticated
using (
  bucket_id = 'resumes' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy: UPDATE
-- Allow update if same conditions as select (ownership)
create policy "Users can update their own resumes"
on storage.objects for update
to authenticated
using (
  bucket_id = 'resumes' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy: DELETE
-- Allow delete if same conditions as select (ownership)
create policy "Users can delete their own resumes"
on storage.objects for delete
to authenticated
using (
  bucket_id = 'resumes' AND
  (storage.foldername(name))[1] = auth.uid()::text
);
