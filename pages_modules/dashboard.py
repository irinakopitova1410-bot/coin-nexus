import streamlit as st
from services.db import get_dashboard_stats, get_recent_analyses

def show_dashboard():
    tenant = st.session_state.get("tenant", {})

    st.markdown("""
    <div style="background:linear-gradient(135deg,#1E40AF,#7C3AED);padding:25px;border-radius:12px;margin-bottom:25px;">
        <h1 style="color:white;margin:0;font-size:1.8rem;">🏠 Dashboard Direzionale</h1>
        <p style="color:#BFDBFE;margin:5px 0 0 0;">Panoramica completa delle analisi finanziarie in tempo reale</p>
    </div>
    """, unsafe_allow_html=True)

    stats = get_dashboard_stats(tenant.get("id", ""))
    total = sum(stats.values())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⚠️ Analisi Rischio", stats.get("risk", 0))
    with col2:
        st.metric("💳 Credit Report", stats.get("credit", 0))
    with col3:
        st.metric("📊 Audit Report", stats.get("audit", 0))
    with col4:
        st.metric("📋 Totale Analisi", total)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚠️ Ultime Analisi Rischio")
        data = get_recent_analyses("analisi_rischio", 5)
        if data:
            for item in data:
                z = item.get("z_score", 0) or 0
                name = item.get("company_name") or item.get("azienda") or "N/A"
                color = "#4ADE80" if z > 2.9 else "#FCD34D" if z > 1.23 else "#F87171"
                date = (item.get("created_at") or "")[:10]
                st.markdown(f"""
                <div style="background:#1E293B;border-radius:8px;padding:12px;margin:5px 0;border-left:3px solid {color};">
                    <div style="color:#F1F5F9;font-weight:600;">{name}</div>
                    <div style="color:{color};font-size:0.9rem;">Z-Score: {z:.2f}</div>
                    <div style="color:#64748B;font-size:0.75rem;">{date}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nessuna analisi rischio disponibile")

    with col2:
        st.subheader("💳 Ultimi Credit Report")
        data = get_recent_analyses("credit_reports", 5)
        if data:
            for item in data:
                rating = item.get("rating") or "N/A"
                name = item.get("company_name") or item.get("azienda") or "N/A"
                score = item.get("score") or item.get("credit_score") or 0
                color = "#4ADE80" if score >= 70 else "#FCD34D" if score >= 45 else "#F87171"
                date = (item.get("created_at") or "")[:10]
                st.markdown(f"""
                <div style="background:#1E293B;border-radius:8px;padding:12px;margin:5px 0;border-left:3px solid {color};">
                    <div style="color:#F1F5F9;font-weight:600;">{name}</div>
                    <div style="color:{color};font-size:0.9rem;">Rating: {rating} | Score: {score}</div>
                    <div style="color:#64748B;font-size:0.75rem;">{date}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nessun credit report disponibile")

    st.markdown("---")
    st.subheader("📊 Ultimi Audit Report")
    data = get_recent_analyses("audit_reports", 3)
    if data:
        cols = st.columns(min(3, len(data)))
        for i, item in enumerate(data[:3]):
            with cols[i]:
                name = item.get("company_name") or item.get("azienda") or "N/A"
                score = item.get("score") or 0
                mat = item.get("materiality") or item.get("soglia_materialita") or 0
                color = "#4ADE80" if score >= 85 else "#FCD34D" if score >= 70 else "#F87171"
                st.markdown(f"""
                <div style="background:#1E293B;border-radius:12px;padding:20px;text-align:center;border:1px solid #334155;">
                    <div style="font-size:2rem;font-weight:700;color:{color};">{score}</div>
                    <div style="color:#F1F5F9;font-weight:600;">{name}</div>
                    <div style="color:#94A3B8;font-size:0.8rem;">Materialità: €{mat:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Nessun audit report disponibile")
