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
from utils.ui_kit import page_header, kpi_row, feature_grid, empty_state


def render_dashboard(user: dict):
    role = user.get("role", "client")
    name = user.get("full_name") or user.get("email", "Utente")

    # Header Aurora
    ora = datetime.now().hour
    saluto = "Buongiorno" if ora < 12 else ("Buon pomeriggio" if ora < 18 else "Buonasera")
    giorno_it = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"][datetime.now().weekday()]
    page_header(
        kicker=f"Nexus · Dashboard Esecutiva · {giorno_it} {datetime.now().strftime('%d %B %Y')}",
        title=f"{saluto},",
        highlight=f"{name.split()[0] if name else ''}! 👋",
        subtitle="Tutte le tue analisi, i risultati e le azioni successive — in una sola schermata.",
    )

    # ── Quick actions ──────────────────────────────────────────────────────────
    st.subheader("⚡ Azioni rapide")
    qa = [
        ("🔌 Import ERP", "erp_import", "primary"),
        ("📊 Ratio Analysis", "ratio_analysis", "secondary"),
        ("💰 Cash Flow", "cashflow", "secondary"),
        ("🎯 Z-Score", "risk_analysis", "secondary"),
        ("🏅 Credit Score", "credit_scoring", "secondary"),
    ]
    qcols = st.columns(len(qa))
    for i, (label, page_key, kind) in enumerate(qa):
        with qcols[i]:
            if st.button(label, use_container_width=True,
                         type="primary" if kind == "primary" else "secondary"):
                st.session_state["current_page"] = page_key
                st.rerun()

    st.divider()

    # ── Statistiche DB ─────────────────────────────────────────────────────────
    try:
        sb = get_supabase()
    except Exception:
        sb = None
    stats = {"risk": 0, "credit": 0, "audit": 0}
    if sb:
        try:
            for tbl, label in [
                ("analisi_rischio", "risk"), ("credit_reports", "credit"),
                ("audit_reports", "audit")
            ]:
                r = sb.table(tbl).select("id", count="exact").execute()
                stats[label] = r.count or 0
        except Exception:
            pass

    total = sum(stats.values())

    # ── KPI Bar ──────────────────────────────────────────────────────────────
    kpi_row([
        {"label": "Analisi totali", "value": str(total),
         "sub": "Tutte le analisi registrate", "tone": "blue"},
        {"label": "Z-Score calcolati", "value": str(stats.get("risk", 0)),
         "sub": "Modelli Altman eseguiti", "tone": ""},
        {"label": "Credit report", "value": str(stats.get("credit", 0)),
         "sub": "Rating e readiness prodotti", "tone": ""},
        {"label": "Audit report", "value": str(stats.get("audit", 0)),
         "sub": "Revisioni ISA 320 completate", "tone": ""},
    ])

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
                empty_state("📭", "Nessuna analisi ancora",
                            "Inizia con Import ERP o chiedi al Copilot: «come sta la mia azienda?»")
        except Exception as e:
            empty_state("📭", "Nessuna analisi ancora",
                        "Inizia con Import ERP o chiedi al Copilot: «come sta la mia azienda?»")

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
                             color_discrete_sequence=["#1E376C"])
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
                marker_colors=["#1E376C", "#0D9488", "#D97706"],
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
            | Ricavi | {fmt(erp_data.get('ricavi_netti') or erp_data.get('revenue'))} |
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
                st.session_state["current_page"] = "erp_import"
                st.rerun()

        # Capacità dell'app
        st.subheader("🚀 Funzionalità NEXUS")
        feature_grid([
            {"icon": "🔌", "text": "Import da SAP, Zucchetti, TeamSystem"},
            {"icon": "🎯", "text": "Altman Z-Score (3 modelli)"},
            {"icon": "📊", "text": "35+ Ratio finanziari"},
            {"icon": "💰", "text": "Cash Flow con proiezioni 5 anni"},
            {"icon": "🛡️", "text": "Covenant bancari monitor"},
            {"icon": "🏅", "text": "Credit Scoring + Rating"},
            {"icon": "📄", "text": "Audit Report automatico"},
            {"icon": "📑", "text": "Export PDF professionale"},
            {"icon": "🧭", "text": "Benchmark di settore"},
            {"icon": "◆", "text": "Copilot AI nativo"},
        ])
