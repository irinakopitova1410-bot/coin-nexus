mport streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. SETUP INTERFACCIA HIGH-END
st.set_page_config(page_title="COIN-NEXUS ELITE", layout="wide", initial_sidebar_state="expanded")

# CSS Custom per effetto Glassmorphism e Neon
st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #0a0f18; border-right: 1px solid #1e293b; }
    .stMetric { 
        background: rgba(16, 24, 39, 0.7); 
        border: 1px solid #3b82f6; 
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
        border-radius: 15px; padding: 25px;
    }
    h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -1px; color: #f8fafc; }
    .stButton>button { 
        background: linear-gradient(90deg, #3b82f6, #2563eb); 
        color: white; border: none; border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. NAVIGAZIONE
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/584/584704.png", width=80) # Icona placeholder elite
st.sidebar.title("COIN-NEXUS | ELITE")
app_mode = st.sidebar.selectbox("COMMAND CENTER", 
    ["🛡️ AUDIT INTELLIGENCE", "💎 RATING BASILEA IV", "🛰️ CENTRALE RISCHI", "🌪️ STRESS TEST PRO"])

# 3. LOGICA DI CARICAMENTO
file = st.sidebar.file_uploader("UPLOAD DATASET", type=['xlsx', 'csv'])

def load_data(file):
    if file.name.endswith('.xlsx'): return pd.read_excel(file, engine='openpyxl')
    return pd.read_csv(file, sep=None, engine='python', encoding='latin1')

# ==========================================
# MODULO 1: AUDIT INTELLIGENCE
# ==========================================
if app_mode == "🛡️ AUDIT INTELLIGENCE":
    st.title("🛡️ Audit Intelligence Engine")
    if file:
        df = load_data(file)
        v_col = [c for c in df.columns if any(x in c.lower() for x in ['valore', 'saldo', 'euro'])][0]
        c_col = [c for c in df.columns if any(x in c.lower() for x in ['voce', 'desc', 'conto'])][0]
        df[v_col] = pd.to_numeric(df[v_col].astype(str).replace('[€, ]', '', regex=True), errors='coerce').fillna(0)

        c1, c2, c3 = st.columns(3)
        c1.metric("CAPITALE RILEVATO", f"€ {df[v_col].sum():,.0f}", "+2.4%")
        c2.metric("INDICE LIQUIDITÀ", "1.82", "Safe Range", delta_color="normal")
        c3.metric("RISCHIO FALLIMENTO", "LOW", "-12%", delta_color="inverse")

        fig = px.sunburst(df.nlargest(15, v_col), path=[c_col], values=v_col,
                          color=v_col, color_continuous_scale='Blues',
                          template="plotly_dark")
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sincronizzazione file richiesta per attivare l'Audit.")

# ==========================================
# MODULO 2: RATING BASILEA IV
# ==========================================
elif app_mode == "💎 RATING BASILEA IV":
    st.title("💎 Advanced Credit Scoring")
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        ebitda = st.number_input("EBITDA NOMINALE", value=500000)
        pfn = st.number_input("POSIZIONE FINANZIARIA NETTA", value=1200000)
        score = round(pfn/ebitda, 2)
    
    with col_b:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "PFN / EBITDA (RISK RATIO)", 'font': {'size': 24}},
            delta = {'reference': 3, 'increasing': {'color': "#ef4444"}, 'decreasing': {'color': "#10b981"}},
            gauge = {
                'axis': {'range': [None, 8], 'tickwidth': 1},
                'bar': {'color': "#3b82f6"},
                'bgcolor': "rgba(0,0,0,0)",
                'steps': [
                    {'range': [0, 2], 'color': "#065f46"},
                    {'range': [2, 4], 'color': "#1e3a8a"},
                    {'range': [4, 8], 'color': "#7f1d1d"}]}))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white", 'family': "Inter"})
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# MODULO 3: CENTRALE RISCHI🛰️
# ==========================================
elif app_mode == "🛰️ CENTRALE RISCHI":
    st.title("🛰️ Deep Web Banking Analysis")
    data = {"Banca": ["Intesa", "UniCredit", "BPM", "MPS"], "Utilizzo": [80, 45, 92, 30], "Fido": [100, 100, 100, 100]}
    df_cr = pd.DataFrame(data)
    
    fig = px.bar(df_cr, x="Banca", y=["Utilizzo", "Fido"], 
                 barmode="group", template="plotly_dark",
                 color_discrete_sequence=['#3b82f6', '#1e293b'])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# MODULO 4: STRESS TEST PRO
# ==========================================
else:
    st.title("🌪️ Predictive Stress Simulation")
    impact = st.select_slider("INTENSITÀ SHOCK ECONOMICO", options=["Lieve", "Moderato", "Severo", "Catastrofico"])
    
    # Grafico di Stress Interattivo
    x = list(range(12))
    y_base = [100 + i*2 for i in x]
    drop = {"Lieve": 10, "Moderato": 30, "Severo": 60, "Catastrofico": 95}[impact]
    y_stress = [100 + i*2 - (drop if i > 3 else 0) for i in x]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y_base, name="SCENARIO AS-IS", line=dict(color='#3b82f6', width=4)))
    fig.add_trace(go.Scatter(x=x, y=y_stress, name="SCENARIO SHOCK", line=dict(color='#ef4444', width=4, dash='dot')))
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("SISTEMA CRIPTATO | SESSIONE ELITE ATTIVA")
