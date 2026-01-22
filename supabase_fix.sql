
-- =============================================================================
-- NEXUS CAREER AI - SCRIPT DE CORREÇÃO E ATUALIZAÇÃO (ROBUSTO)
-- =============================================================================
-- Este script tenta corrigir problemas de permissão e garantir que todas as
-- tabelas e buckets existam. Ele usa blocos de tratamento de erro para ignorar
-- falhas de permissão em objetos que já existem ou pertencem a outros usuários.
-- =============================================================================

-- 1. EXTENSÕES
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. FUNÇÃO AUXILIAR PARA CRIAR TABELAS (Evita erros de permissão se já existirem)
DO $$ 
BEGIN 
    -- Tabela Profiles
    CREATE TABLE IF NOT EXISTS public.profiles (
        id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
        full_name TEXT,
        linkedin_url TEXT,
        portfolio_url TEXT,
        target_role TEXT,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    );
    -- Tenta ajustar o dono para o usuário atual (postgres) para garantir permissão
    -- Ignora erro se não for possível
    BEGIN
        ALTER TABLE public.profiles OWNER TO postgres;
    EXCEPTION WHEN OTHERS THEN NULL; END;

    -- Tabela Resumes
    CREATE TABLE IF NOT EXISTS public.resumes (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
        file_path TEXT NOT NULL,
        file_name TEXT NOT NULL,
        parsed_content JSONB DEFAULT '{}'::JSONB,
        raw_text TEXT,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    );
    BEGIN
        ALTER TABLE public.resumes OWNER TO postgres;
    EXCEPTION WHEN OTHERS THEN NULL; END;

    -- Tabela Job Descriptions
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'job_status') THEN
        CREATE TYPE public.job_status AS ENUM ('saved', 'applied', 'interviewing', 'offer', 'rejected');
    END IF;

    CREATE TABLE IF NOT EXISTS public.job_descriptions (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        url TEXT,
        raw_text TEXT,
        status public.job_status DEFAULT 'saved',
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    );
    BEGIN
        ALTER TABLE public.job_descriptions OWNER TO postgres;
    EXCEPTION WHEN OTHERS THEN NULL; END;

    -- Tabela Analyses
    CREATE TABLE IF NOT EXISTS public.analyses (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
        resume_id UUID REFERENCES public.resumes(id) ON DELETE CASCADE,
        job_description_id UUID REFERENCES public.job_descriptions(id) ON DELETE CASCADE,
        match_score INTEGER CHECK (match_score >= 0 AND match_score <= 100),
        summary TEXT,
        created_at TIMESTAMPTZ DEFAULT now()
    );
    BEGIN
        ALTER TABLE public.analyses OWNER TO postgres;
    EXCEPTION WHEN OTHERS THEN NULL; END;
END $$;

-- 3. HABILITAR RLS (Segurança)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;

-- 4. POLÍTICAS DE SEGURANÇA (PUBLIC TABLES)
-- Usamos DO blocks para remover políticas antigas apenas se tivermos permissão
DO $$ 
BEGIN
    -- Profiles
    BEGIN DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles; EXCEPTION WHEN OTHERS THEN NULL; END;
    BEGIN DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles; EXCEPTION WHEN OTHERS THEN NULL; END;
    
    CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT USING (auth.uid() = id);
    CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);

    -- Resumes
    BEGIN DROP POLICY IF EXISTS "Users can all own resumes" ON public.resumes; EXCEPTION WHEN OTHERS THEN NULL; END;
    CREATE POLICY "Users can all own resumes" ON public.resumes FOR ALL USING (auth.uid() = user_id);

    -- Job Descriptions
    BEGIN DROP POLICY IF EXISTS "Users can all own job descriptions" ON public.job_descriptions; EXCEPTION WHEN OTHERS THEN NULL; END;
    CREATE POLICY "Users can all own job descriptions" ON public.job_descriptions FOR ALL USING (auth.uid() = user_id);

    -- Analyses
    BEGIN DROP POLICY IF EXISTS "Users can all own analyses" ON public.analyses; EXCEPTION WHEN OTHERS THEN NULL; END;
    CREATE POLICY "Users can all own analyses" ON public.analyses FOR ALL USING (auth.uid() = user_id);
END $$;

-- 5. TRIGGER DE USUÁRIO (PERFIL AUTOMÁTICO)
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name)
  VALUES (new.id, new.raw_user_meta_data->>'full_name')
  ON CONFLICT (id) DO NOTHING;
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Remove trigger antigo se existir e recria
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- 6. STORAGE (BUCKET E POLÍTICAS)
-- Tenta criar o bucket 'resumes'
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES ('resumes', 'resumes', false, 5242880, ARRAY['application/pdf'])
ON CONFLICT (id) DO UPDATE SET 
  public = false,
  file_size_limit = 5242880,
  allowed_mime_types = ARRAY['application/pdf'];

-- Políticas de Storage (A parte mais sensível a erros 42501)
DO $$ 
BEGIN
    -- INSERT Policy
    BEGIN 
        DROP POLICY IF EXISTS "Users can upload their own resumes" ON storage.objects; 
    EXCEPTION WHEN OTHERS THEN 
        RAISE NOTICE 'Não foi possível remover política antiga de INSERT (pode não ser sua). Tentando criar...';
    END;
    
    BEGIN
        CREATE POLICY "Users can upload their own resumes" ON storage.objects FOR INSERT TO authenticated
        WITH CHECK (bucket_id = 'resumes' AND (storage.foldername(name))[1] = auth.uid()::text);
    EXCEPTION WHEN OTHERS THEN 
        RAISE NOTICE 'Política de INSERT já existe ou erro de permissão.';
    END;

    -- SELECT Policy
    BEGIN 
        DROP POLICY IF EXISTS "Users can view their own resumes" ON storage.objects; 
    EXCEPTION WHEN OTHERS THEN NULL; 
    END;
    
    BEGIN
        CREATE POLICY "Users can view their own resumes" ON storage.objects FOR SELECT TO authenticated
        USING (bucket_id = 'resumes' AND (storage.foldername(name))[1] = auth.uid()::text);
    EXCEPTION WHEN OTHERS THEN NULL; 
    END;

    -- DELETE Policy
    BEGIN 
        DROP POLICY IF EXISTS "Users can delete their own resumes" ON storage.objects; 
    EXCEPTION WHEN OTHERS THEN NULL; 
    END;
    
    BEGIN
        CREATE POLICY "Users can delete their own resumes" ON storage.objects FOR DELETE TO authenticated
        USING (bucket_id = 'resumes' AND (storage.foldername(name))[1] = auth.uid()::text);
    EXCEPTION WHEN OTHERS THEN NULL; 
    END;
END $$;

