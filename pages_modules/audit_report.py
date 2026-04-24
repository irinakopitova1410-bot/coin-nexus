import streamlit as st
import pandas as pd
import io
from engine.calculations import calculate_audit
from services.db import save_audit_report, get_recent_analyses

# ─────────────────────────────────────────────────────────────
#  CAMPI ACCETTATI DAL PARSER (CSV / Excel)
# ─────────────────────────────────────────────────────────────
FIELD_MAP = {
    # nome_azienda
    "azienda": "company_name", "nome_azienda": "company_name",
    "company": "company_name", "company_name": "company_name",
    # gross_profit
    "utile_lordo": "gross_profit", "gross_profit": "gross_profit",
    "utile lordo": "gross_profit", "profit": "gross_profit",
    # total_assets
    "totale_attivo": "total_assets", "total_assets": "total_assets",
    "totale attivo": "total_assets", "assets": "total_assets",
    # net_revenue
    "ricavi_netti": "net_revenue", "net_revenue": "net_revenue",
    "ricavi netti": "net_revenue", "fatturato": "net_revenue",
    "revenue": "net_revenue",
    # pre_tax_income
    "reddito_ante_imposte": "pre_tax_income", "pre_tax_income": "pre_tax_income",
    "reddito ante imposte": "pre_tax_income", "ebt": "pre_tax_income",
    # internal_control_score
    "controlli_interni": "internal_control_score",
    "internal_control_score": "internal_control_score",
    "controlli interni": "internal_control_score",
    # error_rate
    "tasso_errori": "error_rate", "error_rate": "error_rate",
    "tasso errori": "error_rate", "errori": "error_rate",
    # risk_level
    "rischio": "risk_level", "risk_level": "risk_level",
    "livello_rischio": "risk_level", "livello rischio": "risk_level",
}

AUDIT_TEMPLATE_CSV = """campo,valore
azienda,La Mia SRL
utile_lordo,250000
totale_attivo,2000000
ricavi_netti,1500000
reddito_ante_imposte,200000
controlli_interni,7
tasso_errori,2.0
rischio,medium
"""

def _parse_audit_file(uploaded_file) -> dict | None:
    """Legge CSV o Excel e restituisce dict con i campi audit normalizzati."""
    try:
        name = uploaded_file.name.lower()
        if name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        data = {}

        # Formato colonnare: campo | valore
        if df.shape[1] == 2:
            col_key = df.columns[0].lower().strip()
            col_val = df.columns[1].lower().strip()
            if col_key in ("campo", "field", "key", "nome") and col_val in ("valore", "value", "val"):
                for _, row in df.iterrows():
                    raw_key = str(row.iloc[0]).strip().lower()
                    raw_val = str(row.iloc[1]).strip()
                    mapped = FIELD_MAP.get(raw_key)
                    if mapped:
                        data[mapped] = raw_val
            else:
                # Formato riga singola: colonne = campi
                df.columns = [c.lower().strip() for c in df.columns]
                for col in df.columns:
                    mapped = FIELD_MAP.get(col)
                    if mapped:
                        data[mapped] = str(df[col].iloc[0]).strip()
        else:
            # Più colonne: prima riga = dati
            df.columns = [c.lower().strip() for c in df.columns]
            for col in df.columns:
                mapped = FIELD_MAP.get(col)
                if mapped:
                    data[mapped] = str(df[col].iloc[0]).strip()

        return data if data else None
    except Exception as e:
        st.error(f"Errore lettura file: {e}")
        return None


def _safe_float(val, default=0.0):
    try:
        return float(str(val).replace(",", ".").replace("€", "").replace(" ", ""))
    except Exception:
        return default


def _safe_int(val, default=7, min_v=1, max_v=10):
    try:
        v = int(float(str(val)))
        return max(min_v, min(max_v, v))
    except Exception:
        return default


def _normalize_risk(val: str) -> str:
    v = str(val).lower().strip()
    if v in ("low", "basso", "l"):
        return "low"
    if v in ("high", "alto", "h"):
        return "high"
    return "medium"


def _show_audit_result(result, company_name: str, key_suffix: str = ""):
    """Renderizza i risultati di un audit calcolato."""
    st.markdown(f"""
    <div style="background:#1E293B;border:2px solid {result.judgment_color};
         border-radius:12px;padding:20px;margin:15px 0;text-align:center;">
        <div style="font-size:1.4rem;font-weight:700;color:{result.judgment_color};">
            {result.judgment}
        </div>
        <div style="color:#94A3B8;margin-top:5px;">Score Qualità: {result.score}/100</div>
        {"<div style='color:#60A5FA;margin-top:4px;font-size:0.9rem;'>🏢 " + company_name + "</div>" if company_name else ""}
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background:#1E293B;border-radius:12px;padding:20px;text-align:center;">
            <div style="color:#94A3B8;font-size:0.8rem;">SOGLIA DI MATERIALITÀ</div>
            <div style="color:#3B82F6;font-size:1.6rem;font-weight:700;">€{result.materiality:,.2f}</div>
            <div style="color:#64748B;font-size:0.75rem;">5% × Utile Lordo</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background:#1E293B;border-radius:12px;padding:20px;text-align:center;">
            <div style="color:#94A3B8;font-size:0.8rem;">PERFORMANCE MATERIALITY</div>
            <div style="color:#8B5CF6;font-size:1.6rem;font-weight:700;">€{result.performance_materiality:,.2f}</div>
            <div style="color:#64748B;font-size:0.75rem;">75%/80%/65% della Materialità</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background:#1E293B;border-radius:12px;padding:20px;text-align:center;">
            <div style="color:#94A3B8;font-size:0.8rem;">SOGLIA DI IRRILEVANZA</div>
            <div style="color:#06B6D4;font-size:1.6rem;font-weight:700;">€{result.trivial_threshold:,.2f}</div>
            <div style="color:#64748B;font-size:0.75rem;">3% della Materialità</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("⚠️ Rischi Identificati")
        for risk in result.risks:
            st.markdown(f"- {risk}")
    with c2:
        st.subheader("💡 Raccomandazioni")
        for rec in result.recommendations:
            st.markdown(f"- {rec}")


# ─────────────────────────────────────────────────────────────
#  PAGINA PRINCIPALE
# ─────────────────────────────────────────────────────────────
def show_audit_report():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#4C1D95,#7C3AED);padding:25px;border-radius:12px;margin-bottom:25px;">
        <h1 style="color:white;margin:0;font-size:1.8rem;">📊 Audit Report — ISA 320</h1>
        <p style="color:#DDD6FE;margin:5px 0 0 0;">Calcolo materialità, performance materiality e giudizio di revisione</p>
    </div>
    """, unsafe_allow_html=True)

    access_token = st.session_state.get("access_token", None)

    tab_upload, tab_form, tab_storico = st.tabs([
        "⚡ Carica & Analizza",
        "📝 Nuovo Audit (Form)",
        "📋 Storico Audit"
    ])

    # ══════════════════════════════════════════════════════════
    #  TAB 1 — CARICA & ANALIZZA
    # ══════════════════════════════════════════════════════════
    with tab_upload:
        st.markdown("""
        <div style="background:linear-gradient(90deg,#4C1D95,#6D28D9);
             border-radius:10px;padding:18px 22px;margin-bottom:18px;">
            <h3 style="color:white;margin:0;">⚡ Carica il bilancio → Audit immediato</h3>
            <p style="color:#DDD6FE;margin:6px 0 0 0;font-size:0.9rem;">
                Carica un file CSV o Excel con i dati aziendali e ottieni
                materialità, performance materiality e giudizio ISA 320 in un click.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Template scaricabile
        tmpl_bytes = AUDIT_TEMPLATE_CSV.encode("utf-8")
        st.download_button(
            label="📥 Scarica Template CSV",
            data=tmpl_bytes,
            file_name="template_audit_ISA320.csv",
            mime="text/csv",
            use_container_width=True,
        )

        uploaded = st.file_uploader(
            "📂 Carica CSV o Excel",
            type=["csv", "xlsx", "xls"],
            key="audit_upload",
            help="Il file deve contenere: utile_lordo, totale_attivo, ricavi_netti, reddito_ante_imposte, controlli_interni, tasso_errori, rischio",
        )

        if uploaded is not None:
            data = _parse_audit_file(uploaded)
            if data is None:
                st.error("❌ File non riconosciuto. Usa il template CSV scaricabile.")
            else:
                company_name = data.get("company_name", "Azienda da file")
                gross_profit = _safe_float(data.get("gross_profit", 250000))
                total_assets = _safe_float(data.get("total_assets", 2000000))
                net_revenue = _safe_float(data.get("net_revenue", 1500000))
                pre_tax_income = _safe_float(data.get("pre_tax_income", 200000))
                internal_control_score = _safe_int(data.get("internal_control_score", 7))
                error_rate = _safe_float(data.get("error_rate", 2.0))
                risk_level = _normalize_risk(data.get("risk_level", "medium"))

                # Mostra dati letti
                with st.expander("📋 Dati letti dal file", expanded=False):
                    preview = {
                        "Azienda": company_name,
                        "Utile Lordo (€)": f"€{gross_profit:,.0f}",
                        "Totale Attivo (€)": f"€{total_assets:,.0f}",
                        "Ricavi Netti (€)": f"€{net_revenue:,.0f}",
                        "Reddito ante Imposte (€)": f"€{pre_tax_income:,.0f}",
                        "Controlli Interni (1-10)": internal_control_score,
                        "Tasso Errori (%)": f"{error_rate:.1f}%",
                        "Livello Rischio": {"low": "🟢 Basso", "medium": "🟡 Medio", "high": "🔴 Alto"}[risk_level],
                    }
                    st.table(pd.DataFrame(list(preview.items()), columns=["Campo", "Valore"]))

                # Calcolo immediato
                result = calculate_audit(
                    gross_profit, total_assets, net_revenue, pre_tax_income,
                    internal_control_score, error_rate, risk_level
                )

                st.markdown("---")
                st.markdown("### 📊 Risultati Audit ISA 320")
                _show_audit_result(result, company_name, key_suffix="upload")

                # Auto-salvataggio
                saved = save_audit_report({
                    "company_name": company_name,
                    "gross_profit": gross_profit,
                    "total_assets": total_assets,
                    "net_revenue": net_revenue,
                    "revenue": net_revenue,
                    "pre_tax_income": pre_tax_income,
                    "materiality": result.materiality,
                    "performance_materiality": result.performance_materiality,
                    "trivial_threshold": result.trivial_threshold,
                    "score": result.score,
                    "rating": result.judgment,
                    "judgment": result.judgment,
                    "risk_level": risk_level,
                    "internal_control_score": internal_control_score,
                    "error_rate": error_rate,
                }, access_token=access_token)

                if saved:
                    st.toast("💾 Audit report salvato su Supabase!", icon="✅")
                else:
                    st.warning("⚠️ Calcolato ma non salvato — effettua il login per salvare.")

    # ══════════════════════════════════════════════════════════
    #  TAB 2 — FORM MANUALE
    # ══════════════════════════════════════════════════════════
    with tab_form:
        company_name = st.text_input("Nome Azienda", placeholder="Es: Tech Innovations S.r.l.", key="audit_company_manual")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📈 Dati di Bilancio")
            gross_profit = st.number_input("Utile Lordo (€)", value=250000.0, step=10000.0, format="%.0f", key="audit_gp")
            total_assets = st.number_input("Totale Attivo (€)", value=2000000.0, step=50000.0, format="%.0f", key="audit_ta")
            net_revenue = st.number_input("Ricavi Netti (€)", value=1500000.0, step=50000.0, format="%.0f", key="audit_rev")
            pre_tax_income = st.number_input("Reddito ante imposte (€)", value=200000.0, step=10000.0, format="%.0f", key="audit_pti")

        with col2:
            st.subheader("🔍 Parametri di Revisione")
            internal_control_score = st.slider(
                "Qualità Controlli Interni", 1, 10, 7,
                help="1=Pessimo, 10=Eccellente", key="audit_ics"
            )
            error_rate = st.number_input(
                "Tasso di Errori Rilevati (%)", min_value=0.0, max_value=100.0,
                value=2.0, step=0.5, format="%.1f", key="audit_er"
            )
            risk_level = st.select_slider(
                "Livello di Rischio Inerente",
                options=["low", "medium", "high"],
                value="medium",
                format_func=lambda x: {"low": "🟢 Basso", "medium": "🟡 Medio", "high": "🔴 Alto"}[x],
                key="audit_rl"
            )
            st.markdown("---")
            st.markdown("""
            **Guida ISA 320:**
            - Materialità = 5% utile lordo
            - Performance Mat. = 75% materialità
            - Soglia irrilevanza = 3% materialità
            """)

        st.markdown("---")

        if st.button("📊 GENERA AUDIT REPORT", type="primary", use_container_width=True, key="audit_submit_manual"):
            result = calculate_audit(
                gross_profit, total_assets, net_revenue, pre_tax_income,
                internal_control_score, error_rate, risk_level
            )

            _show_audit_result(result, company_name, key_suffix="manual")

            saved = save_audit_report({
                "company_name": company_name or "N/A",
                "gross_profit": gross_profit,
                "total_assets": total_assets,
                "net_revenue": net_revenue,
                "revenue": net_revenue,
                "pre_tax_income": pre_tax_income,
                "materiality": result.materiality,
                "performance_materiality": result.performance_materiality,
                "trivial_threshold": result.trivial_threshold,
                "score": result.score,
                "rating": result.judgment,
                "judgment": result.judgment,
                "risk_level": risk_level,
                "internal_control_score": internal_control_score,
                "error_rate": error_rate,
            }, access_token=access_token)

            if saved:
                st.toast("💾 Audit report salvato su Supabase!", icon="✅")
            else:
                st.warning("⚠️ Calcolato ma non salvato — effettua il login per salvare.")

    # ══════════════════════════════════════════════════════════
    #  TAB 3 — STORICO
    # ══════════════════════════════════════════════════════════
    with tab_storico:
        st.subheader("📋 Storico Audit Reports")

        records = get_recent_analyses("audit_reports", limit=50, access_token=access_token)

        if not records:
            st.info("Nessun audit report salvato ancora. Genera il primo dalla tab '⚡ Carica & Analizza'!")
        else:
            df = pd.DataFrame(records)

            col_map = {
                "created_at": "Data",
                "company_name": "Azienda",
                "judgment": "Giudizio",
                "score": "Score",
                "materiality": "Materialità (€)",
                "performance_materiality": "Perf. Mat. (€)",
                "risk_level": "Rischio",
                "internal_control_score": "Ctrl Interni",
                "error_rate": "Errori %",
            }
            cols_show = [c for c in col_map.keys() if c in df.columns]
            df_show = df[cols_show].rename(columns=col_map)

            if "Data" in df_show.columns:
                df_show["Data"] = pd.to_datetime(df_show["Data"]).dt.strftime("%d/%m/%Y %H:%M")
            if "Materialità (€)" in df_show.columns:
                df_show["Materialità (€)"] = df_show["Materialità (€)"].apply(
                    lambda x: f"€{x:,.2f}" if pd.notna(x) else "—"
                )
            if "Perf. Mat. (€)" in df_show.columns:
                df_show["Perf. Mat. (€)"] = df_show["Perf. Mat. (€)"].apply(
                    lambda x: f"€{x:,.2f}" if pd.notna(x) else "—"
                )

            st.dataframe(df_show, use_container_width=True)

            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Tot. Audit", len(df))
            with col2:
                if "score" in df.columns:
                    st.metric("⭐ Score Medio", f"{df['score'].mean():.0f}/100")
            with col3:
                if "risk_level" in df.columns:
                    alto = (df["risk_level"] == "high").sum()
                    st.metric("🔴 Rischio Alto", alto)
