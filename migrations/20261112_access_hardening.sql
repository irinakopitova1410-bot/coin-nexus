-- NEXUS only. No financial row or existing profile is changed/deleted.
-- Profiles must not grant themselves admin, move tenants or reactivate themselves.
CREATE OR REPLACE FUNCTION public.protect_profile_security_fields()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
  IF auth.role() = 'authenticated' AND NOT public.is_admin() THEN
    IF TG_OP = 'INSERT' THEN
      IF NEW.role IS DISTINCT FROM 'client' OR NEW.tenant_id IS NOT NULL
         OR NEW.is_active IS DISTINCT FROM true THEN
        RAISE EXCEPTION 'Profile security fields are managed by administrators';
      END IF;
    ELSIF NEW.id IS DISTINCT FROM OLD.id OR NEW.role IS DISTINCT FROM OLD.role
       OR NEW.tenant_id IS DISTINCT FROM OLD.tenant_id
       OR NEW.is_active IS DISTINCT FROM OLD.is_active THEN
      RAISE EXCEPTION 'Profile security fields are managed by administrators';
    END IF;
  END IF;
  RETURN NEW;
END;
$$;
REVOKE ALL ON FUNCTION public.protect_profile_security_fields() FROM PUBLIC;
CREATE TRIGGER nexus_profile_security_guard
BEFORE INSERT OR UPDATE ON public.user_profiles
FOR EACH ROW EXECUTE FUNCTION public.protect_profile_security_fields();

-- Ownerless legacy records are not public records. Administrators retain access.
DROP POLICY "Nexus Access Policy" ON public.credit_analyses;
CREATE POLICY nexus_credit_analyses_admin ON public.credit_analyses
FOR ALL TO authenticated USING (public.is_admin()) WITH CHECK (public.is_admin());

-- This legacy table has no owner column: do not expose its contents publicly.
DROP POLICY "Permetti lettura a tutti" ON public.reports;
DROP POLICY "Permetti inserimento a tutti" ON public.reports;
CREATE POLICY nexus_reports_admin_only ON public.reports
FOR ALL TO authenticated USING (public.is_admin()) WITH CHECK (public.is_admin());

DROP POLICY analisi_rischio_insert ON public.analisi_rischio;
CREATE POLICY nexus_risk_owned_insert ON public.analisi_rischio
FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid() OR public.is_admin());

CREATE POLICY nexus_credit_reports_admin_select ON public.credit_reports
FOR SELECT TO authenticated USING (public.is_admin());
