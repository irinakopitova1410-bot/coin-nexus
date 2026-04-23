import streamlit as st
import pandas as pd
from engine.calculations import altman_z_original, altman_z_prime, altman_z_doubleprime
from utils.charts import gauge_chart, projection_chart
from utils.file_parser import parse_zscore_file, get_zscore_template_bytes
from services.db import save_risk_analysis

def show_risk_analysis():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#7C2D12,#C2410C);padding:25px;border-radius:12px;margin-bottom:25px;">
        <h1 style="color:white;margin:0;font-size:1.8rem;">⚠️ Analisi del Rischio — Altman Z-Score</h1>
        <p style="color:#FED7AA;margin:5px 0 0 0;">Previsione fallimento con 3 modelli scientifici validati</p>
    </div>
    """, unsafe_allow_html=True)

    model_choice = st.radio(
        "Seleziona Modello",
        ["Z-Score (1968) — Quotate manifatturiere",
         "Z'-Score (1983) — Aziende private (PMI) ⭐",
         "Z''-Score (1995) — Servizi/Non manifatturiere"],
        index=1
    )

    st.markdown("---")

    # ─── Upload File ──────────────────────────────────────────────────────────
    st.subheader("📂 Carica Dati da File")
    col_up, col_tmpl = st.columns([3, 1])
    with col_up:
        uploaded = st.file_uploader(
            "Carica CSV o Excel con i dati del bilancio",
            type=["csv", "xlsx", "xls"],
            help="Usa il template scaricabile per il formato corretto",
            key="zscore_upload"
        )
    with col_tmpl:
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            "📥 Scarica Template CSV",
            data=get_zscore_template_bytes(),
            file_name="template_zscore.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Valori di default
    defaults = {
        "nome_azienda": "",
        "total_assets": 1000000.0,
        "retained_earnings": 100000.0,
        "ebit": 80000.0,
        "working_capital": 150000.0,
        "total_liabilities": 500000.0,
        "equity_input": 500000.0,
        "revenue": 800000.0,
    }

    if uploaded:
        parsed = parse_zscore_file(uploaded)
        if parsed["success"]:
            defaults.update(parsed)
            st.success(f"✅ File caricato! Dati importati per: **{parsed.get('nome_azienda', 'Azienda')}**")
        else:
            st.error(f"❌ Errore nel file: {parsed['error']}. Usa il template CSV.")

    st.markdown("---")

    # ─── Inserimento Dati ─────────────────────────────────────────────────────
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📝 Dati Aziendali")
        company_name = st.text_input("Nome Azienda", value=defaults["nome_azienda"], placeholder="Es: Rossi S.r.l.")

        colA, colB = st.columns(2)
        with colA:
            total_assets      = st.number_input("Totale Attivo (€)",                  min_value=0.0, value=float(defaults["total_assets"]),      step=10000.0, format="%.0f")
            retained_earnings = st.number_input("Utili non distribuiti / Riserve (€)",               value=float(defaults["retained_earnings"]),   step=10000.0, format="%.0f")
            ebit              = st.number_input("EBIT — Reddito Operativo (€)",                       value=float(defaults["ebit"]),                step=5000.0,  format="%.0f")
            working_capital   = st.number_input("Capitale Circolante Netto (€)",                      value=float(defaults["working_capital"]),      step=10000.0, format="%.0f")
        with colB:
            total_liabilities = st.number_input("Totale Passività (€)",               min_value=1.0, value=float(defaults["total_liabilities"]),  step=10000.0, format="%.0f")
            if "Quotate" in model_choice:
                equity_input  = st.number_input("Market Cap (€)",                                     value=float(defaults["equity_input"]),         step=10000.0, format="%.0f")
            else:
                equity_input  = st.number_input("Patrimonio Netto Contabile (€)",                     value=float(defaults["equity_input"]),         step=10000.0, format="%.0f")
            revenue           = st.number_input("Ricavi Netti (€)",                   min_value=0.0, value=float(defaults["revenue"]),             step=10000.0, format="%.0f")

    with col2:
        st.subheader("ℹ️ Come interpretare")
        if "Z'-Score (1983)" in model_choice:
            st.info("**Modello Z' (1983)**\nIdeal per PMI italiane\n\n🟢 Z > 2.9 → Sicuro\n🟡 1.23–2.9 → Grigio\n🔴 Z < 1.23 → Pericolo")
        elif "Quotate" in model_choice:
            st.info("**Modello Z (1968)**\nAziende quotate in borsa\n\n🟢 Z > 2.99 → Sicuro\n🟡 1.81–2.99 → Grigio\n🔴 Z < 1.81 → Pericolo")
        else:
            st.info("**Modello Z'' (1995)**\nServizi e non manifatturiere\n\n🟢 Z > 2.6 → Sicuro\n🟡 1.1–2.6 → Grigio\n🔴 Z < 1.1 → Pericolo")

    st.markdown("---")

    if st.button("🔍 CALCOLA Z-SCORE", type="primary", use_container_width=True):
        try:
            if "Z'-Score (1983)" in model_choice:
                result = altman_z_prime(working_capital, total_assets, retained_earnings,
                                         ebit, equity_input, total_liabilities, revenue)
            elif "Quotate" in model_choice:
                result = altman_z_original(working_capital, total_assets, retained_earnings,
                                            ebit, equity_input, total_liabilities, revenue)
            else:
                result = altman_z_doubleprime(working_capital, total_assets, retained_earnings,
                                               ebit, equity_input, total_liabilities)

            zone_bg  = {"safe": "#14532D", "grey": "#422006", "distress": "#450A0A"}[result.zone]
            zone_txt = {"safe": "#4ADE80", "grey": "#FCD34D", "distress": "#F87171"}[result.zone]

            st.markdown(f"""
            <div style="background:{zone_bg};border:2px solid {zone_txt};border-radius:12px;padding:20px;margin:15px 0;">
                <div style="text-align:center;">
                    <div style="font-size:3rem;font-weight:800;color:{zone_txt};">{result.z_score}</div>
                    <div style="color:{zone_txt};font-size:1.2rem;font-weight:700;">{result.zone_label}</div>
                    <div style="color:#CBD5E1;font-size:0.9rem;margin-top:5px;">{result.model}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(gauge_chart(result.z_score, "Z-Score", 0, 5, result.thresholds), use_container_width=True)
            with col2:
                st.markdown(f"""
                <div style="background:#1E293B;border-radius:12px;padding:20px;">
                    <h3 style="color:#F1F5F9;margin-top:0;">📊 Indicatori Chiave</h3>
                    <div style="margin:10px 0;padding:10px;background:#0F172A;border-radius:8px;">
                        <div style="color:#94A3B8;font-size:0.8rem;">PROBABILITÀ DI DEFAULT</div>
                        <div style="color:{zone_txt};font-size:1.8rem;font-weight:700;">{result.bankruptcy_probability:.1f}%</div>
                    </div>
                    <div style="margin:10px 0;padding:10px;background:#0F172A;border-radius:8px;">
                        <div style="color:#94A3B8;font-size:0.8rem;">RATING IMPLICITO</div>
                        <div style="color:#3B82F6;font-size:1.8rem;font-weight:700;">{result.rating}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.subheader("🧮 Scomposizione Variabili")
            var_cols = st.columns(len(result.variables))
            for i, (k, v) in enumerate(result.variables.items()):
                with var_cols[i]:
                    color = "#4ADE80" if v > 0 else "#F87171"
                    st.markdown(f"""
                    <div style="background:#1E293B;border-radius:8px;padding:12px;text-align:center;">
                        <div style="color:#94A3B8;font-size:0.75rem;">{k}</div>
                        <div style="color:{color};font-size:1.3rem;font-weight:700;">{v:.4f}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#1E293B;border-left:4px solid {zone_txt};border-radius:8px;padding:15px;margin:15px 0;">
                <strong style="color:#F1F5F9;">📋 Raccomandazione</strong><br>
                <span style="color:#CBD5E1;">{result.recommendation}</span>
            </div>
            """, unsafe_allow_html=True)

            st.plotly_chart(projection_chart(result.projections), use_container_width=True)

            df_proj = pd.DataFrame(result.projections)
            st.dataframe(df_proj.set_index("Anno"), use_container_width=True)

            st.markdown("---")
            if st.button("💾 Salva Analisi su Supabase"):
                saved = save_risk_analysis({
                    "company_name": company_name or "N/A",
                    "model": result.model,
                    "z_score": result.z_score,
                    "zone": result.zone,
                    "bankruptcy_probability": result.bankruptcy_probability,
                    "rating": result.rating,
                    "total_assets": total_assets,
                    "total_liabilities": total_liabilities,
                    "ebit": ebit,
                    "revenue": revenue,
                })
                if saved:
                    st.success("✅ Analisi salvata con successo!")

        except Exception as e:
            st.error(f"❌ Errore nel calcolo: {e}. Verifica che i valori inseriti siano corretti.")
