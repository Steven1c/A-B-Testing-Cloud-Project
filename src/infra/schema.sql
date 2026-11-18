SKEMA DATABASE
Kepuasan Pembelajaran: Luring (Varian A) vs Daring (Varian B)
    
-- 1. Buat tabel survey_responses
CREATE TABLE IF NOT EXISTS public.survey_responses (
    -- Identitas respon & sesi anonim
    response_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(64) NOT NULL UNIQUE,
    variant_group CHAR(1) NOT NULL CHECK (variant_group IN ('A', 'B')),
    variant CHAR(1) CHECK (variant IN ('A', 'B')),
    
    -- Metrik Utama Inferensial H0 vs H1 (Skala Likert 1-5)
    score SMALLINT NOT NULL CHECK (score BETWEEN 1 AND 5),
    
    -- Dimensi 1: Kepuasan & Efektivitas Keseluruhan
    sat_overall SMALLINT CHECK (sat_overall BETWEEN 1 AND 5),
    sat_expectation SMALLINT CHECK (sat_expectation BETWEEN 1 AND 5),
    sat_effectiveness SMALLINT CHECK (sat_effectiveness BETWEEN 1 AND 5),
    sat_preference SMALLINT CHECK (sat_preference BETWEEN 1 AND 5),
    
    -- Dimensi 2: Pedagogis & Pemahaman Materi
    mat_comprehension SMALLINT CHECK (mat_comprehension BETWEEN 1 AND 5),
    mat_clarity SMALLINT CHECK (mat_clarity BETWEEN 1 AND 5),
    mat_retention SMALLINT CHECK (mat_retention BETWEEN 1 AND 5),
    mat_readiness SMALLINT CHECK (mat_readiness BETWEEN 1 AND 5),
    
    -- Dimensi 3: Interaksi & Keterlibatan Belajar
    int_lecturer SMALLINT CHECK (int_lecturer BETWEEN 1 AND 5),
    int_feedback SMALLINT CHECK (int_feedback BETWEEN 1 AND 5),
    int_peers SMALLINT CHECK (int_peers BETWEEN 1 AND 5),
    int_focus SMALLINT CHECK (int_focus BETWEEN 1 AND 5),
    
    -- Dimensi 4: Fleksibilitas & Kenyamanan Lingkungan
    flx_time SMALLINT CHECK (flx_time BETWEEN 1 AND 5),
    flx_location SMALLINT CHECK (flx_location BETWEEN 1 AND 5),
    flx_comfort SMALLINT CHECK (flx_comfort BETWEEN 1 AND 5),
    flx_pace SMALLINT CHECK (flx_pace BETWEEN 1 AND 5),
    
    -- Dimensi 5: Dukungan Teknis & Kelancaran Operasional
    tec_access SMALLINT CHECK (tec_access BETWEEN 1 AND 5),
    tec_stability SMALLINT CHECK (tec_stability BETWEEN 1 AND 5),
    tec_submission SMALLINT CHECK (tec_submission BETWEEN 1 AND 5),
    tec_attendance SMALLINT CHECK (tec_attendance BETWEEN 1 AND 5),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Trigger sinkronisasi otomatis antara variant dan variant_group
CREATE OR REPLACE FUNCTION public.sync_variant_columns()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.variant_group IS NULL AND NEW.variant IS NOT NULL THEN
        NEW.variant_group := NEW.variant;
    ELSIF NEW.variant IS NULL AND NEW.variant_group IS NOT NULL THEN
        NEW.variant := NEW.variant_group;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_variant_columns
BEFORE INSERT ON public.survey_responses
FOR EACH ROW
EXECUTE FUNCTION public.sync_variant_columns();

-- 3. Index untuk optimasi query agregasi analisis A/B
CREATE INDEX IF NOT EXISTS idx_survey_variant ON public.survey_responses (variant_group);
CREATE INDEX IF NOT EXISTS idx_survey_created_at ON public.survey_responses (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_survey_score ON public.survey_responses (score);

-- 4. Row Level Security (RLS)
ALTER TABLE public.survey_responses ENABLE ROW LEVEL SECURITY;

-- Izinkan publik/responden anonim memasukkan data survei
CREATE POLICY "Allow anonymous inserts" 
ON public.survey_responses 
FOR INSERT 
TO anon 
WITH CHECK (true);

-- Izinkan pembacaan data untuk agregasi dashboard analisis
CREATE POLICY "Allow anonymous read for analysis" 
ON public.survey_responses 
FOR SELECT 
TO anon 
USING (true);
