import streamlit as st
import pandas as pd
from services.db import get_all_history
from utils.ui_kit import page_header

def show_history():
    page_header(
        kicker="Archivio · Supabase",
        title="Storico",
        highlight="Analisi",
        subtitle="Z-Score, Credit Report e Audit Report — ogni analisi salvata, datata e ricercabile.",
    )

    tab1, tab2, tab3 = st.tabs(["⚠️ Analisi Rischio", "💳 Credit Report", "📊 Audit Report"])

    data = get_all_history()

    with tab1:
        risk_data = data.get("analisi_rischio", [])
        if risk_data:
            df = pd.DataFrame(risk_data)
            cols_show = [c for c in ["created_at","company_name","model","z_score","zone","bankruptcy_probability","rating"] if c in df.columns]
            if cols_show:
                df_show = df[cols_show].copy()
                if "created_at" in df_show.columns:
                    df_show["created_at"] = pd.to_datetime(df_show["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
                df_show.columns = [c.replace("_"," ").title() for c in df_show.columns]
                st.dataframe(df_show, use_container_width=True)
                st.caption(f"Totale: {len(df)} analisi")
            else:
                st.dataframe(pd.DataFrame(risk_data), use_container_width=True)
        else:
            st.info("Nessuna analisi rischio trovata. Esegui una nuova analisi dalla sezione ⚠️ Analisi Rischio.")

    with tab2:
        credit_data = data.get("credit_reports", [])
        if credit_data:
            df = pd.DataFrame(credit_data)
            cols_show = [c for c in ["created_at","company_name","score","rating","decision","dscr","leverage","ebitda_margin","max_credit"] if c in df.columns]
            if cols_show:
                df_show = df[cols_show].copy()
                if "created_at" in df_show.columns:
                    df_show["created_at"] = pd.to_datetime(df_show["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
                df_show.columns = [c.replace("_"," ").title() for c in df_show.columns]
                st.dataframe(df_show, use_container_width=True)
                st.caption(f"Totale: {len(df)} credit report")
            else:
                st.dataframe(pd.DataFrame(credit_data), use_container_width=True)
        else:
            st.info("Nessun credit report trovato. Esegui una nuova analisi dalla sezione 💳 Credit Scoring.")

    with tab3:
        audit_data = data.get("audit_reports", [])
        if audit_data:
            df = pd.DataFrame(audit_data)
            cols_show = [c for c in ["created_at","company_name","materiality","performance_materiality","score","judgment","risk_level"] if c in df.columns]
            if cols_show:
                df_show = df[cols_show].copy()
                if "created_at" in df_show.columns:
                    df_show["created_at"] = pd.to_datetime(df_show["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
                df_show.columns = [c.replace("_"," ").title() for c in df_show.columns]
                st.dataframe(df_show, use_container_width=True)
                st.caption(f"Totale: {len(df)} audit report")
            else:
                st.dataframe(pd.DataFrame(audit_data), use_container_width=True)
        else:
            st.info("Nessun audit report trovato. Esegui una nuova analisi dalla sezione 📊 Audit Report.")
