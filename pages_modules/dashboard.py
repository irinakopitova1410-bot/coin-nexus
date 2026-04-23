"""
NEXUS Finance Pro — Executive Dashboard
Panoramica completa: statistiche, ultimi report, attività recente.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from services.db import get_supabase


def render_dashboard(user: dict):
    role = user.get("role", "client")
    name = user.get("full_name") or user.get("email", "Utente")

    # Header
    ora = datetime.now().hour
    saluto = "Buongiorno" if ora < 12 else ("Buon pomeriggio" if ora < 18 else "Buonasera")
    st.markdown(f"""
    <div class="nexus-header">
        <div style='font-size:1.6rem; font-weight:700;'>{saluto}, {name.split()[0] if name else ""}! 👋</div>
        <div style='font-size:0.95rem; opacity:0.85; margin-top:0.3rem;'>
            NEXUS Finance Pro — Dashboard Esecutiva &nbsp;|&nbsp; {datetime.now().strftime("%A %d %B %Y")}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick actions ──────────────────────────────────────────────────────────
    st.subheader("⚡ Azioni Rapide")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🔌 Import ERP", use_container_width=True, type="primary"):
            st.session_state["nav_page"] = "🔌 Import da ERP"
            st.rerun()
    with col2:
        if st.button("📊 Ratio Analysis", use_container_width=True):
            st.session_state["nav_page"] = "📊 Ratio Analysis"
            st.rerun()
    with col3:
        if st.button("💰 Cash Flow", use_container_width=True):
            st.session_state["nav_page"] = "💰 Cash Flow"
            st.rerun()
    with col4:
        if st.button("🎯 Z-Score", use_container_width=True):
            st.session_state["nav_page"] = "🎯 Z-Score Altman"
            st.rerun()
    with col5:
        if st.button("🏅 Credit Score", use_container_width=True):
            st.session_state["nav_page"] = "🏅 Credit Scoring"
            st.rerun()

    st.divider()

    # ── Statistiche DB ─────────────────────────────────────────────────────────
    sb = get_supabase()
    stats = {}
    try:
        for tbl, label in [
            ("analisi_rischio", "risk"), ("credit_reports", "credit"),
            ("audit_reports", "audit")
        ]:
            r = sb.table(tbl).select("id", count="exact").execute()
            stats[label] = r.count or 0
    except:
        stats = {"risk": 0, "credit": 0, "audit": 0}

    total = sum(stats.values())

    # ── KPI Bar ──────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Analisi Totali", total)
    col2.metric("🎯 Z-Score Calcolati", stats.get("risk", 0))
    col3.metric("🏅 Credit Report", stats.get("credit", 0))
    col4.metric("📄 Audit Report", stats.get("audit", 0))

    # ── Layout 2 colonne ────────────────────────────────────────────────────────
    col_left, col_right = st.columns([3, 2])

    with col_left:
        # Attività recente
        st.subheader("📋 Attività Recente")
        try:
            rows = []
            for tbl, tipo in [("analisi_rischio", "🎯 Z-Score"), ("credit_reports", "🏅 Credit"), ("audit_reports", "📄 Audit")]:
                r = sb.table(tbl).select("*").order("created_at", desc=True).limit(4).execute()
                for item in (r.data or []):
                    rows.append({
                        "Tipo": tipo,
                        "Azienda": item.get("company_name", item.get("azienda", "—")),
                        "Data": item.get("created_at", "")[:10] if item.get("created_at") else "—",
                        "Risultato": str(item.get("z_score", item.get("score", item.get("rating", "—")))),
                    })
            if rows:
                df = pd.DataFrame(rows).sort_values("Data", ascending=False).head(12)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("📭 Nessuna analisi ancora. Inizia con Import ERP o una nuova analisi!")
        except Exception as e:
            st.info("📭 Nessuna analisi ancora. Inizia con Import ERP o una nuova analisi!")

        # Grafico attività nel tempo
        st.subheader("📈 Andamento Analisi")
        try:
            all_dates = []
            for tbl in ["analisi_rischio", "credit_reports", "audit_reports"]:
                r = sb.table(tbl).select("created_at").execute()
                for item in (r.data or []):
                    if item.get("created_at"):
                        all_dates.append(item["created_at"][:10])
            if all_dates:
                df_dates = pd.DataFrame({"data": all_dates})
                df_dates["data"] = pd.to_datetime(df_dates["data"])
                df_count = df_dates.groupby("data").size().reset_index(name="n")
                fig = px.bar(df_count, x="data", y="n", title="Analisi per giorno",
                             color_discrete_sequence=["#0D47A1"])
                fig.update_layout(height=250, showlegend=False,
                                  xaxis_title="", yaxis_title="Analisi")
                st.plotly_chart(fig, use_container_width=True)
        except:
            pass

    with col_right:
        # Distribuzione analisi
        st.subheader("🍩 Distribuzione")
        if total > 0:
            fig_pie = go.Figure(go.Pie(
                labels=["Z-Score", "Credit", "Audit"],
                values=[stats["risk"], stats["credit"], stats["audit"]],
                hole=0.5,
                marker_colors=["#0D47A1", "#00897B", "#F57C00"],
                textinfo="label+percent",
            ))
            fig_pie.update_layout(height=300, showlegend=False,
                                   margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Nessun dato ancora")

        # ERP status
        st.subheader("🔌 Stato Import ERP")
        if st.session_state.get("erp_data"):
            company = st.session_state.get("erp_company", "Azienda")
            erp_data = st.session_state["erp_data"]
            st.success(f"✅ **{company}** caricata")
            fmt = lambda v: f"€ {float(v):,.0f}" if v else "—"
            st.markdown(f"""
            | Voce | Valore |
            |------|--------|
            | Ricavi | {fmt(erp_data.get('revenue'))} |
            | EBITDA | {fmt(erp_data.get('ebitda'))} |
            | Totale Attivo | {fmt(erp_data.get('total_assets'))} |
            | Patr. Netto | {fmt(erp_data.get('equity'))} |
            """)
            if st.button("🔄 Nuova Analisi (reset dati)", use_container_width=True):
                st.session_state.pop("erp_data", None)
                st.session_state.pop("erp_company", None)
                st.rerun()
        else:
            st.info("Nessun dato ERP caricato.")
            if st.button("🔌 Importa da ERP ora", use_container_width=True, type="primary"):
                st.session_state["nav_page"] = "🔌 Import da ERP"
                st.rerun()

        # Capacità dell'app
        st.subheader("🚀 Funzionalità NEXUS")
        features = [
            "✅ Import da SAP, Zucchetti, TeamSystem",
            "✅ Altman Z-Score (3 modelli)",
            "✅ 35+ Ratio finanziari",
            "✅ Cash Flow con proiezioni 5 anni",
            "✅ Covenant bancari monitor",
            "✅ Credit Scoring + Rating",
            "✅ Audit Report automatico",
            "✅ Export PDF professionale",
            "✅ Benchmark di settore",
        ]
        for f in features:
            st.markdown(f"<div style='font-size:0.85rem; padding:2px 0;'>{f}</div>",
                       unsafe_allow_html=True)
