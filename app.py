import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ... (Mantieni il CSS e il setup precedente) ...

# AGGIUNGI QUESTO NUOVO MODULO AL MENU DELLA SIDEBAR
# menu = st.sidebar.radio("MODULI OPERATIVI", ["💎 RIEPILOGO ESECUTIVO", "🕵️ RISCHIO REVISIONE (BIG4)", "🛡️ SCUDO DI RISCHIO", "📈 PROIEZIONI FLUSSI"])

# ==========================================
# MODULO NUOVO: RISCHIO REVISIONE (STILE DELOITTE)
# ==========================================
if menu == "🕵️ RISCHIO REVISIONE (BIG4)":
    st.title("🕵️ Valutazione Professionale del Rischio di Revisione")
    st.markdown("---")
    
    col_input, col_viz = st.columns([1, 1])
    
    with col_input:
        st.subheader("Parametri di Valutazione")
        ir = st.select_slider("Rischio Intrinseco (Inherent Risk)", 
                              options=[0.1, 0.3, 0.5, 0.8, 1.0], value=0.5,
                              help="Rischio legato alla natura dell'attività e al settore.")
        
        cr = st.select_slider("Rischio di Controllo (Control Risk)", 
                              options=[0.1, 0.3, 0.5, 0.8, 1.0], value=0.3,
                              help="Efficacia dei sistemi di controllo interno dell'azienda.")
        
        # Calcolo Detection Risk necessario per mantenere un Audit Risk accettabile (es. 5%)
        audit_risk_target = 0.05
        dr_necessario = round(audit_risk_target / (ir * cr), 2)
        
    with col_viz:
        st.subheader("Matrice di Rischio Professionale")
        # Formula: AR = IR * CR * DR
        rischio_totale = ir * cr
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = rischio_totale * 100,
            title = {'text': "Rischio Combinato (IR x CR) %"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "#00d4ff"},
                'steps': [
                    {'range': [0, 20], 'color': "green"},
                    {'range': [20, 50], 'color': "yellow"},
                    {'range': [50, 100], 'color': "red"}]}))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("📝 Strategia di Revisione Consigliata")
    
    if dr_necessario < 0.2:
        st.error(f"⚠️ **ATTENZIONE:** Il rischio combinato è altissimo. È necessario un Detection Risk molto basso ({dr_necessario}). Richieste procedure di revisione massive e campionamento esteso.")
    elif dr_necessario < 0.5:
        st.warning(f"🟡 **PROCEDURE STANDARD:** Detection Risk richiesto: {dr_necessario}. Si consigliano test di sostanza moderati sui saldi di bilancio.")
    else:
        st.success(f"✅ **PROCEDURE ANALITICHE:** Detection Risk richiesto: {dr_necessario}. È possibile fare affidamento sui controlli interni e limitare i test diretti.")
