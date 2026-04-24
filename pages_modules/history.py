import streamlit as st
import pandas as pd
from services.db import get_all_history

def show_history():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#134E4A,#0F766E);padding:25px;border-radius:12px;margin-bottom:25px;">
        <h1 style="color:white;margin:0;font-size:1.8rem;">📋 Storico Analisi</h1>
        <p style="color:#99F6E4;margin:5px 0 0 0;">Tutte le analisi salvate nel tuo Supabase</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["⚠️ Analisi Rischio", "💳 Credit Report", "📊 Audit Report"])

    # Passa il JWT per rispettare RLS (ogni utente vede solo i propri dati)
    access_token = st.session_state.get("access_token", "")
    data = get_all_history(access_token=access_token)

    with tab1:
        risk_data = data.get("analisi_rischio", [])
        if risk_data:
            df = pd.DataFrame(risk_data)
            cols_show = [c for c in ["created_at", "company_name", "model", "z_score", "zone",
                                      "bankruptcy_probability", "rating", "total_assets",
                                      "revenue", "ebit"] if c in df.columns]
            if cols_show:
                df_show = df[cols_show].copy()
                if "created_at" in df_show.columns:
                    df_show["created_at"] = pd.to_datetime(df_show["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
                # Formatta colonne numeriche
                for col in ["z_score", "bankruptcy_probability", "total_assets", "revenue", "ebit"]:
                    if col in df_show.columns:
                        df_show[col] = df_show[col].apply(
                            lambda x: f"{x:,.2f}" if pd.notna(x) else "-"
                        )
                df_show.columns = [c.replace("_", " ").title() for c in df_show.columns]
                df_show = df_show.rename(columns={
                    "Bankruptcy Probability": "Prob. Fallimento (%)",
                    "Total Assets": "Totale Attivo (€)",
                    "Revenue": "Ricavi (€)",
                    "Ebit": "EBIT (€)",
                    "Z Score": "Z-Score",
                    "Created At": "Data",
                    "Company Name": "Azienda",
                })
                st.dataframe(df_show, use_container_width=True)
                st.caption(f"💾 Totale: **{len(df)} analisi** salvate in Supabase")

                # Grafico Z-Score nel tempo
                if "z_score" in df.columns and "created_at" in df.columns:
                    st.subheader("📈 Andamento Z-Score nel tempo")
                    df_chart = df[["created_at", "company_name", "z_score"]].copy()
                    df_chart["created_at"] = pd.to_datetime(df_chart["created_at"])
                    df_chart = df_chart.dropna(subset=["z_score"]).sort_values("created_at")
                    if not df_chart.empty:
                        import plotly.express as px
                        fig = px.line(df_chart, x="created_at", y="z_score",
                                      color="company_name", markers=True,
                                      labels={"created_at": "Data", "z_score": "Z-Score",
                                              "company_name": "Azienda"},
                                      title="Z-Score storico per azienda")
                        fig.add_hline(y=2.9, line_color="green", line_dash="dot",
                                      annotation_text="Soglia sicura (Z'=2.9)")
                        fig.add_hline(y=1.23, line_color="orange", line_dash="dot",
                                      annotation_text="Soglia grigia (Z'=1.23)")
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(pd.DataFrame(risk_data), use_container_width=True)
        else:
            st.info("Nessuna analisi rischio trovata. Esegui una nuova analisi dalla sezione ⚠️ Analisi Rischio.")

    with tab2:
        credit_data = data.get("credit_reports", [])
        if credit_data:
            df = pd.DataFrame(credit_data)
            cols_show = [c for c in ["created_at", "company_name", "credit_score", "rating",
                                      "decision", "dscr", "leverage", "margin",
                                      "estimated_credit_amount", "risk_level"] if c in df.columns]
            if cols_show:
                df_show = df[cols_show].copy()
                if "created_at" in df_show.columns:
                    df_show["created_at"] = pd.to_datetime(df_show["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
                df_show.columns = [c.replace("_", " ").title() for c in df_show.columns]
                st.dataframe(df_show, use_container_width=True)
                st.caption(f"💾 Totale: **{len(df)} credit report** salvati in Supabase")
            else:
                st.dataframe(pd.DataFrame(credit_data), use_container_width=True)
        else:
            st.info("Nessun credit report trovato. Esegui una nuova analisi dalla sezione 💳 Credit Scoring.")

    with tab3:
        audit_data = data.get("audit_reports", [])
        if audit_data:
            df = pd.DataFrame(audit_data)
            cols_show = [c for c in ["created_at", "company_name", "materiality",
                                      "score", "rating", "revenue"] if c in df.columns]
            if cols_show:
                df_show = df[cols_show].copy()
                if "created_at" in df_show.columns:
                    df_show["created_at"] = pd.to_datetime(df_show["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
                df_show.columns = [c.replace("_", " ").title() for c in df_show.columns]
                st.dataframe(df_show, use_container_width=True)
                st.caption(f"💾 Totale: **{len(df)} audit report** salvati in Supabase")
            else:
                st.dataframe(pd.DataFrame(audit_data), use_container_width=True)
        else:
            st.info("Nessun audit report trovato. Esegui una nuova analisi dalla sezione 📊 Audit Report.")
