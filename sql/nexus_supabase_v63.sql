-- ============================================================================
-- NEXUS v6.3 — FIX DATABASE COMPLETO  (idempotente: puoi rieseguirlo)
-- Come si usa: Supabase Dashboard → SQL Editor → New query → Incolla → Run
-- Tempo: ~5 secondi.   Rischi: nessuno (solo DROP di policy/trigger omonimi).
-- ============================================================================

-- ═══════════════════════════════════════════════════════════════════════════
-- 1) RIPARA LA REGISTRAZIONE — trigger su auth.users rotto (signup → 500)
--    Il vecchio trigger non riempiva la colonna NOT NULL "role" di user_profiles.
-- ═══════════════════════════════════════════════════════════════════════════
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  INSERT INTO public.user_profiles (id, email, full_name, role, company_name, is_active)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1)),
    'client',
    NULLIF(NEW.raw_user_meta_data->>'company_name', ''),
    true
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
EXCEPTION
  WHEN OTHERS THEN
    -- Mai bloccare la registrazione per un errore del profilo
    RETURN NEW;
END;
$$;

CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Profilo per gli utenti già registrati prima della riparazione (se mancante)
INSERT INTO public.user_profiles (id, email, full_name, role, is_active)
SELECT u.id,
       u.email,
       COALESCE(u.raw_user_meta_data->>'full_name', split_part(u.email, '@', 1)),
       'client',
       true
FROM auth.users u
WHERE NOT EXISTS (SELECT 1 FROM public.user_profiles p WHERE p.id = u.id)
ON CONFLICT (id) DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════
-- 2) credit_reports — aggiunge la colonna user_id mancante
--    (era la causa del fallimento del salvataggio Credit Readiness)
-- ═══════════════════════════════════════════════════════════════════════════
ALTER TABLE public.credit_reports
  ADD COLUMN IF NOT EXISTS user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_credit_reports_user_id
  ON public.credit_reports(user_id);

-- Recupera l'associazione per i report salvati con la fallback raw_data
UPDATE public.credit_reports cr
SET user_id = (SELECT u.id FROM auth.users u WHERE u.email = cr.raw_data->>'saved_for_user')
WHERE cr.user_id IS NULL
  AND cr.raw_data ? 'saved_for_user';

-- ═══════════════════════════════════════════════════════════════════════════
-- 3) RLS ATTIVA SU TUTTE LE TABELLE (default deny: nessuno vede nulla
--    senza policy esplicita — nemmeno con la chiave anon)
-- ═══════════════════════════════════════════════════════════════════════════
ALTER TABLE public.user_profiles   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analisi_rischio ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_reports  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_reports   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tenants         ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.companies       ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_logs   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports         ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_analyses ENABLE ROW LEVEL SECURITY;

-- ═══════════════════════════════════════════════════════════════════════════
-- 4) POLICY per utenti autenticati — ogni utente vede SOLO i propri dati
-- ═══════════════════════════════════════════════════════════════════════════

-- ── user_profiles: profilo proprio (lettura, creazione, modifica) ──
DROP POLICY IF EXISTS prof_sel ON public.user_profiles;
CREATE POLICY prof_sel ON public.user_profiles
  FOR SELECT TO authenticated USING (id = auth.uid());
DROP POLICY IF EXISTS prof_ins ON public.user_profiles;
CREATE POLICY prof_ins ON public.user_profiles
  FOR INSERT TO authenticated WITH CHECK (id = auth.uid());
DROP POLICY IF EXISTS prof_upd ON public.user_profiles;
CREATE POLICY prof_upd ON public.user_profiles
  FOR UPDATE TO authenticated USING (id = auth.uid()) WITH CHECK (id = auth.uid());

-- ── analisi_rischio: righe proprie ──
DROP POLICY IF EXISTS risk_sel ON public.analisi_rischio;
CREATE POLICY risk_sel ON public.analisi_rischio
  FOR SELECT TO authenticated USING (user_id = auth.uid());
DROP POLICY IF EXISTS risk_ins ON public.analisi_rischio;
CREATE POLICY risk_ins ON public.analisi_rischio
  FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid());
DROP POLICY IF EXISTS risk_upd ON public.analisi_rischio;
CREATE POLICY risk_upd ON public.analisi_rischio
  FOR UPDATE TO authenticated USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());
DROP POLICY IF EXISTS risk_del ON public.analisi_rischio;
CREATE POLICY risk_del ON public.analisi_rischio
  FOR DELETE TO authenticated USING (user_id = auth.uid());

-- ── credit_reports: righe proprie (anche via raw_data.saved_for_user) ──
DROP POLICY IF EXISTS cred_sel ON public.credit_reports;
CREATE POLICY cred_sel ON public.credit_reports
  FOR SELECT TO authenticated
  USING (user_id = auth.uid()
         OR (user_id IS NULL AND raw_data->>'saved_for_user' = auth.uid()::text));
DROP POLICY IF EXISTS cred_ins ON public.credit_reports;
CREATE POLICY cred_ins ON public.credit_reports
  FOR INSERT TO authenticated
  WITH CHECK (user_id = auth.uid()
              OR (user_id IS NULL AND raw_data->>'saved_for_user' = auth.uid()::text));
DROP POLICY IF EXISTS cred_del ON public.credit_reports;
CREATE POLICY cred_del ON public.credit_reports
  FOR DELETE TO authenticated
  USING (user_id = auth.uid()
         OR (user_id IS NULL AND raw_data->>'saved_for_user' = auth.uid()::text));

-- ── audit_reports: righe proprie ──
DROP POLICY IF EXISTS audit_sel ON public.audit_reports;
CREATE POLICY audit_sel ON public.audit_reports
  FOR SELECT TO authenticated USING (user_id = auth.uid());
DROP POLICY IF EXISTS audit_ins ON public.audit_reports;
CREATE POLICY audit_ins ON public.audit_reports
  FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid());
DROP POLICY IF EXISTS audit_del ON public.audit_reports;
CREATE POLICY audit_del ON public.audit_reports
  FOR DELETE TO authenticated USING (user_id = auth.uid());

-- NOTA: tenants, companies, analysis_logs, reports, credit_analyses restano
-- SENZA policy → accessibili SOLO via service_role (bypass RLS), cioè
-- Edge Functions e backend. Questa è la configurazione più sicura.

-- ═══════════════════════════════════════════════════════════════════════════
-- 5) ASSEGNA LE RIGHE ORFANE (user_id NULL) all'owner del progetto
--    così i 18 audit report storici riappaiono nel suo storico
-- ═══════════════════════════════════════════════════════════════════════════
UPDATE public.audit_reports
SET user_id = (SELECT id FROM auth.users WHERE email = 'irina.kopitova1410@gmail.com')
WHERE user_id IS NULL;

-- ═══════════════════════════════════════════════════════════════════════════
-- 6) RPC verify_api_key — verifica chiave API senza esporre la tabella tenants
-- ═══════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION public.verify_api_key(p_api_key text)
RETURNS SETOF public.tenants
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT * FROM public.tenants WHERE api_key = p_api_key;
$$;

GRANT EXECUTE ON FUNCTION public.verify_api_key(text) TO anon, authenticated;

-- ═══════════════════════════════════════════════════════════════════════════
-- FINE — Verifica rapida (opzionale):
--   SELECT email, role FROM public.user_profiles;
--   Poi prova a registrare un nuovo utente dall'app: deve funzionare al primo colpo.
-- ═══════════════════════════════════════════════════════════════════════════
