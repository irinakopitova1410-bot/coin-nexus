# --- SEZIONE BILANCIO & RISCHIO (Migliorata per chiarezza) ---
st.subheader("🛡️ Rating di Solidità Aziendale")
totale_impegni = df['Valore_Euro'].sum()
indice_solidita = (cassa_reale / totale_impegni * 100) if totale_impegni > 0 else 100

col_top1, col_top2 = st.columns([1, 1])

with col_top1:
    st.markdown("### Riepilogo Finanziario")
    st.metric("Liquidità in Cassa", f"€ {cassa_reale:,}")
    st.metric("Debiti Totali (Sistemi)", f"€ {totale_impegni:,}", delta=f"{int(indice_solidita)}% Copertura", delta_color="normal")
    
    # Messaggio di testo chiaro basato sul rischio
    if indice_solidita > 120:
        st.success("✅ SITUAZIONE OTTIMALE: La cassa copre ampiamente i debiti.")
    elif indice_solidita > 80:
        st.warning("⚠️ ATTENZIONE: Liquidità al limite. Monitorare le scadenze SAP.")
    else:
        st.error("🚨 RISCHIO ALTO: Debiti superiori alla cassa. Urgente recupero crediti.")

with col_top2:
    # Tachimetro del Rischio PIÙ GRANDE E CHIARO
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = indice_solidita,
        number = {'suffix': "%", 'font': {'size': 40}},
        gauge = {
            'axis': {'range': [0, 200], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "white"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps' : [
                {'range': [0, 80], 'color': "#ff4b4b"},   # Rosso acceso
                {'range': [80, 120], 'color': "#ffa500"}, # Arancione
                {'range': [120, 200], 'color': "#00cc96"} # Verde
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': indice_solidita}
        }
    ))
    
    fig_gauge.update_layout(
        height=350, 
        margin=dict(l=30, r=30, t=50, b=0), 
        paper_bgcolor='rgba(0,0,0,0)', 
        font={'color': "white", 'family': "Arial"}
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
