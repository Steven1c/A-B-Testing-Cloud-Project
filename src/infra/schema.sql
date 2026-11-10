-- ====================================================================
-- SKEMA DATABASE: PLATFORM SURVEI DAN UJI A/B
-- Menjalankan di SQL Editor Supabase untuk inisialisasi tabel eksperimen
-- ====================================================================

-- 1. Buat tabel utama survey_responses
CREATE TABLE IF NOT EXISTS public.survey_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL,
    assigned_variant CHAR(1) NOT NULL CHECK (assigned_variant IN ('A', 'B')),
    willingness_to_pay NUMERIC NOT NULL CHECK (willingness_to_pay >= 0),
    perceived_trust INT NOT NULL CHECK (perceived_trust BETWEEN 1 AND 5),
    clicked_signup BOOLEAN NOT NULL DEFAULT FALSE,
    time_spent_sec NUMERIC NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Index untuk optimasi query agregasi analisis A/B
CREATE INDEX IF NOT EXISTS idx_survey_variant ON public.survey_responses (assigned_variant);
CREATE INDEX IF NOT EXISTS idx_survey_created_at ON public.survey_responses (created_at DESC);

-- 3. Row Level Security (RLS)
-- Aktifkan RLS dan beri izin INSERT anonim (pengisi survei) dan SELECT (admin analitik)
ALTER TABLE public.survey_responses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anonymous inserts" 
ON public.survey_responses 
FOR INSERT 
TO anon 
WITH CHECK (true);

CREATE POLICY "Allow anonymous read for analysis" 
ON public.survey_responses 
FOR SELECT 
TO anon 
USING (true);
