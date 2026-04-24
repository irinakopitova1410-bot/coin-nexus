"""
Agentic AI Financial Analyst — XAI (Explainable AI)
Genera commenti testuali professionali sui dati finanziari.
Funziona SENZA API key esterne: usa motore regole proprietario.
"""
import streamlit as st
import pandas as pd
import io
from datetime import datetime


# ─── Motore XAI (regole + template professionali) ─────────────────────────────
def genera_relazione_gestione(dati: dict) -> dict:
    """
    Genera la Relazione sulla Gestione automatica partendo dai dati finanziari.
    Output strutturato come documento professionale (stile Big Four).
    """
    azienda   = dati.get("azienda", "L'azienda")
    anno      = dati.get("anno", datetime.now().year)
    fatturato = dati.get("fatturato", dati.get("ricavi_netti", 0))
    ebitda    = dati.get("ebitda", 0)
    ebit      = dati.get("ebit", ebitda * 0.7)
    utile     = dati.get("utile_netto", ebit * 0.6)
    pn        = dati.get("patrimonio_netto", 0)
    debiti    = dati.get("totale_debiti", 0)
    liquidita = dati.get("liquidita", 0)
    interessi = dati.get("interessi_passivi", 0)
    dso       = dati.get("giorni_incasso_clienti", dati.get("dso", 60))
    dpo       = dati.get("giorni_pagamento_fornitori", dati.get("dpo", 45))
    capex     = dati.get("investimenti_capex", 0)
    dipendenti= dati.get("dipendenti", 0)
    zscore    = dati.get("zscore", None)

    # Calcoli derivati
    ebitda_margin = ebitda / fatturato * 100 if fatturato > 0 else 0
    leva = debiti / pn if pn > 0 else 99
    dscr_proxy = ebitda / (interessi * 1.5) if interessi > 0 else 99
    rot_capitale = fatturato / (debiti + pn) if (debiti + pn) > 0 else 0

    sezioni = {}

    # ── SEZIONE 1: Andamento economico ──────────────────────────────────────
    if fatturato > 0:
        if ebitda_margin >= 15:
            commento_red = (f"**{azienda}** ha conseguito nel {anno} ricavi per "
                           f"**{fatturato:,.0f}€** con un EBITDA margin del **{ebitda_margin:.1f}%**, "
                           f"collocandosi nella fascia alta di redditività per il settore manifatturiero italiano. "
                           f"La generazione di cassa operativa risulta **solida e sostenibile**.")
        elif ebitda_margin >= 8:
            commento_red = (f"**{azienda}** ha registrato ricavi per **{fatturato:,.0f}€** "
                           f"con un EBITDA margin del **{ebitda_margin:.1f}%**, in linea con "
                           f"la media delle PMI italiane del settore. "
                           f"La redditività è **adeguata** ma presenta margini di miglioramento.")
        elif ebitda_margin >= 0:
            commento_red = (f"**{azienda}** ha realizzato ricavi per **{fatturato:,.0f}€** "
                           f"ma con un EBITDA margin contenuto del **{ebitda_margin:.1f}%**. "
                           f"⚠️ La capacità di generare cassa è **sotto la media di settore** "
                           f"(benchmark: 10–15%). Si raccomanda un'analisi strutturale dei costi.")
        else:
            commento_red = (f"**{azienda}** riporta un EBITDA **negativo** ({ebitda:,.0f}€) "
                           f"su ricavi di {fatturato:,.0f}€. 🔴 **Situazione critica**: "
                           f"l'azienda brucia cassa nella gestione ordinaria. "
                           f"Intervento strutturale urgente sui costi fissi.")
    else:
        commento_red = "Dati di fatturato non disponibili per l'analisi della redditività."

    sezioni["📈 Andamento Economico e Redditività"] = commento_red

    # ── SEZIONE 2: Struttura finanziaria ────────────────────────────────────
    if debiti > 0 and pn != 0:
        if pn < 0:
            commento_fin = (f"Il patrimonio netto di **{azienda}** è **negativo** ({pn:,.0f}€), "
                           f"con debiti totali pari a {debiti:,.0f}€. "
                           f"🔴 **Stato di potenziale insolvenza**: il passivo supera l'attivo. "
                           f"Ai sensi dell'art. 2447 c.c., gli amministratori sono obbligati "
                           f"a convocare l'assemblea per deliberare la ricapitalizzazione o lo scioglimento.")
        elif leva > 5:
            commento_fin = (f"La struttura finanziaria mostra una leva elevata (D/E = {leva:.1f}x) "
                           f"con un patrimonio netto di {pn:,.0f}€ a fronte di debiti per {debiti:,.0f}€. "
                           f"⚠️ Il **grado di indebitamento è superiore alla soglia bancaria** (max 3-4x). "
                           f"Le banche potrebbero richiedere garanzie aggiuntive o covenant restrittivi.")
        elif leva > 2:
            commento_fin = (f"La struttura finanziaria presenta una leva moderata (D/E = {leva:.1f}x), "
                           f"con patrimonio netto di {pn:,.0f}€. "
                           f"Il livello di indebitamento è **nella norma per il settore**, "
                           f"pur richiedendo attenzione alla gestione del servizio del debito.")
        else:
            commento_fin = (f"La struttura patrimoniale è **solida**: leva D/E = {leva:.1f}x, "
                           f"ben al di sotto della soglia di allerta. "
                           f"Il patrimonio netto di {pn:,.0f}€ fornisce un'adeguata copertura "
                           f"del rischio e una base solida per accedere al credito bancario.")
    else:
        commento_fin = "Dati patrimoniali insufficienti per l'analisi della struttura finanziaria."

    sezioni["🏦 Struttura Finanziaria e Patrimoniale"] = commento_fin

    # ── SEZIONE 3: Liquidità e capitale circolante ───────────────────────────
    if dso > 0 or dpo > 0:
        delta_wc = dso - dpo
        if delta_wc > 30:
            commento_liq = (f"**Il ciclo del capitale circolante presenta criticità**: "
                           f"i tempi di incasso dai clienti (DSO = **{dso:.0f} giorni**) "
                           f"superano di {delta_wc:.0f} giorni i tempi di pagamento ai fornitori "
                           f"(DPO = {dpo:.0f} giorni). "
                           f"Questo genera un **fabbisogno di liquidità strutturale** "
                           f"che l'azienda deve finanziare con linee di credito a breve termine.")
        elif delta_wc > 0:
            commento_liq = (f"Il ciclo del capitale circolante è **nella norma**: "
                           f"DSO = {dso:.0f} giorni, DPO = {dpo:.0f} giorni. "
                           f"Il gap di {delta_wc:.0f} giorni è gestibile con le linee di fido esistenti.")
        else:
            commento_liq = (f"**Ottima gestione del circolante**: i tempi di pagamento ai fornitori "
                           f"({dpo:.0f} giorni) superano quelli di incasso dai clienti ({dso:.0f} giorni). "
                           f"L'azienda beneficia di un **ciclo finanziario favorevole** "
                           f"(i fornitori finanziano il circolante).")

        if liquidita > 0:
            commento_liq += (f" La liquidità disponibile di **{liquidita:,.0f}€** "
                            f"{'fornisce un cuscinetto adeguato' if liquidita > fatturato * 0.05 else 'appare limitata rispetto ai volumi di attività'}.")
    else:
        commento_liq = "Dati sul ciclo del capitale circolante non disponibili."

    sezioni["💧 Liquidità e Capitale Circolante"] = commento_liq

    # ── SEZIONE 4: Z-Score e rischio default ────────────────────────────────
    if zscore is not None:
        if zscore > 2.99:
            commento_z = (f"Il modello **Z-Score di Altman** assegna a {azienda} un punteggio di "
                         f"**{zscore:.2f}**, collocandosi nella **Zona Sicura** (>2.99). "
                         f"La probabilità di default nei prossimi 2 anni è **inferiore al 5%**. "
                         f"L'azienda presenta fondamentali solidi e un profilo di rischio basso "
                         f"per le istituzioni finanziarie.")
        elif zscore >= 1.81:
            commento_z = (f"Il modello **Z-Score di Altman** assegna un punteggio di **{zscore:.2f}**, "
                         f"nella cosiddetta **Zona Grigia** (1.81–2.99). "
                         f"⚠️ La probabilità di difficoltà finanziarie entro 2 anni è **stimata al 20–50%**. "
                         f"Si raccomanda un monitoraggio trimestrale degli indicatori chiave "
                         f"e la preparazione di un piano di rafforzamento patrimoniale.")
        else:
            commento_z = (f"Il modello **Z-Score di Altman** assegna un punteggio di **{zscore:.2f}**, "
                         f"nella **Zona di Distress** (<1.81). "
                         f"🔴 La probabilità di default entro 24 mesi è **superiore al 70%**. "
                         f"Si raccomanda l'immediata attivazione delle procedure previste "
                         f"dal Codice della Crisi d'Impresa (D.Lgs. 14/2019), "
                         f"inclusa la valutazione di strumenti di composizione negoziata.")
    else:
        commento_z = "Z-Score non calcolabile con i dati forniti. Aggiungere i campi: capitale circolante netto, EBIT, utili non distribuiti."

    sezioni["🎯 Valutazione del Rischio (Z-Score Altman)"] = commento_z

    # ── SEZIONE 5: Prospettive e raccomandazioni ─────────────────────────────
    raccomandazioni = []
    if ebitda_margin < 10 and fatturato > 0:
        raccomandazioni.append("📉 **Ottimizzare la struttura dei costi**: analisi ABC dei costi variabili e fissi per identificare inefficienze")
    if dso > 60:
        raccomandazioni.append(f"⏱️ **Ridurre i tempi di incasso** (attuale DSO={dso:.0f}gg): implementare factoring o solleciti automatici — target DSO < 45 giorni")
    if leva > 4 and pn > 0:
        raccomandazioni.append("🏦 **Ridurre la leva finanziaria**: valutare rifinanziamento a lungo termine o aumento di capitale")
    if pn < 0:
        raccomandazioni.append("🚨 **Ricapitalizzazione urgente**: obbligo ex art. 2447 c.c. — consultare advisor legale entro 30 giorni")
    if dscr_proxy < 1.1 and interessi > 0:
        raccomandazioni.append("⚠️ **DSCR critico**: rinegoziare le scadenze del debito o aumentare EBITDA per mantenere la continuità aziendale")
    if capex > 0 and capex < fatturato * 0.03:
        raccomandazioni.append("🔧 **Investimenti insufficienti**: il CAPEX è sotto il 3% del fatturato — rischio di obsolescenza degli impianti")

    if not raccomandazioni:
        raccomandazioni = ["✅ **Nessuna criticità strutturale rilevata** — continuare con il monitoraggio trimestrale degli KPI"]

    commento_outlook = (
        f"**Raccomandazioni operative per {azienda}:**\n\n" +
        "\n".join(f"{i+1}. {r}" for i, r in enumerate(raccomandazioni))
    )
    sezioni["💡 Raccomandazioni e Piano d'Azione"] = commento_outlook

    return {
        "azienda": azienda,
        "anno": anno,
        "sezioni": sezioni,
        "n_critiche": sum(1 for s in [ebitda_margin < 0, pn < 0,
                                       (zscore is not None and zscore < 1.81),
                                       dscr_proxy < 1.0] if s),
        "rating_testo": (
            "OTTIMO" if ebitda_margin >= 15 and pn > 0 and (zscore is None or zscore > 2.99) else
            "BUONO"  if ebitda_margin >= 8 and pn > 0 else
            "MEDIO"  if ebitda_margin >= 0 and pn > 0 else
            "CRITICO"
        )
    }


# ─── Parse CSV ───────────────────────────────────────────────────────────────
def parse_csv_ai(uploaded_file) -> dict | None:
    try:
        content = uploaded_file.read().decode("utf-8", errors="replace")
        uploaded_file.seek(0)
        lines = [l for l in content.splitlines() if not l.strip().startswith("#") and l.strip()]
        df = pd.read_csv(io.StringIO("\n".join(lines)), header=0)
        df.columns = [str(c).strip().lower() for c in df.columns]
        val_col = "valore" if "valore" in df.columns else df.columns[1]
        data = {str(r[df.columns[0]]).strip().lower(): r[val_col]
                for _, r in df.iterrows() if pd.notna(r[val_col])}

        def g(keys, default=0.0):
            for k in keys:
                if k in data:
                    try:
                        return float(str(data[k]).replace(".", "").replace(",", ".").strip())
                    except:
                        pass
            return default

        return {
            "azienda": str(data.get("azienda", data.get("nome_azienda", "Azienda"))),
            "anno": int(g(["anno"], datetime.now().year)),
            "fatturato": g(["fatturato", "ricavi_netti", "ricavi_vendite"]),
            "ebitda": g(["ebitda", "margine_operativo_lordo"]),
            "ebit": g(["ebit", "risultato_operativo"]),
            "utile_netto": g(["utile_netto", "risultato_netto"]),
            "patrimonio_netto": g(["patrimonio_netto", "equity"]),
            "totale_debiti": g(["totale_debiti", "passivo_totale"]),
            "liquidita": g(["liquidita", "disponibilita_liquide"]),
            "interessi_passivi": g(["interessi_passivi", "oneri_finanziari", "of"]),
            "giorni_incasso_clienti": g(["giorni_incasso_clienti", "dso", "giorni_clienti"]),
            "giorni_pagamento_fornitori": g(["giorni_pagamento_fornitori", "dpo", "giorni_fornitori"]),
            "investimenti_capex": g(["investimenti_capex", "capex", "investimenti"]),
            "dipendenti": g(["dipendenti", "numero_dipendenti"]),
            "zscore": g(["zscore", "z_score", "altman_zscore"], None) or None,
        }
    except Exception as e:
        st.error(f"Errore parsing: {e}")
        return None


# ─── UI ──────────────────────────────────────────────────────────────────────
def show_ai_analyst():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #4f46e5, #7c3aed);
                padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;'>
        <h2 style='color:white; margin:0; font-size:1.8rem;'>🤖 AI Financial Analyst</h2>
        <p style='color: rgba(255,255,255,0.85); margin: 0.3rem 0 0;'>
            Explainable AI · Relazione sulla Gestione automatica · Stile Big Four
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ Come funziona l'AI Analyst?", expanded=False):
        st.markdown("""
        L'**AI Financial Analyst** di Nexus usa un motore di ragionamento proprietario (XAI — Explainable AI) 
        che analizza i tuoi dati finanziari e genera automaticamente:

        - 📝 **Relazione sulla Gestione** — documento narrativo professionale (stile revisore Big Four)
        - 🎯 **Spiegazione del rischio** — "Il rischio è alto PERCHÉ il DSO è 85 giorni e il PN è negativo"
        - 💡 **Raccomandazioni prioritizzate** — azioni concrete con impatto stimato
        - ⚖️ **Riferimenti normativi** — CCII, codice civile, EBA Guidelines

        > **Non è una black box**: ogni valutazione è spiegata con i dati che l'hanno generata.
        """)

    tab_upload, tab_manuale = st.tabs(["⚡ Carica & Analizza", "📝 Inserisci Manualmente"])

    with tab_upload:
        _tab_upload_ai()
    with tab_manuale:
        _tab_manuale_ai()


def _mostra_relazione(relazione: dict):
    """Renderizza la relazione completa in modo professionale."""
    azienda = relazione["azienda"]
    anno    = relazione["anno"]
    rating  = relazione["rating_testo"]
    n_crit  = relazione["n_critiche"]

    color_rating = {
        "OTTIMO": "#22c55e", "BUONO": "#6366f1",
        "MEDIO": "#f59e0b",  "CRITICO": "#ef4444"
    }.get(rating, "#94a3b8")

    st.markdown(f"---")
    st.markdown(f"""
    <div style='background: rgba(0,0,0,0.2); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;'>
        <h3 style='color: white; margin: 0;'>📄 Relazione sulla Gestione — {azienda}</h3>
        <div style='color: #94a3b8; font-size: 0.9rem; margin-top: 0.3rem;'>
            Esercizio {anno} · Generata da AI Financial Analyst Nexus · {datetime.now().strftime("%d/%m/%Y %H:%M")}
        </div>
        <div style='margin-top: 0.8rem;'>
            <span style='background: {color_rating}20; color: {color_rating}; 
                         border: 1px solid {color_rating}40; padding: 4px 12px; 
                         border-radius: 20px; font-weight: 700;'>
                Giudizio complessivo: {rating}
            </span>
            {'<span style="margin-left: 8px; color: #ef4444;">⚠️ ' + str(n_crit) + ' criticità rilevate</span>' if n_crit > 0 else '<span style="margin-left: 8px; color: #22c55e;">✅ Nessuna criticità grave</span>'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    for titolo, testo in relazione["sezioni"].items():
        with st.container():
            st.markdown(f"#### {titolo}")
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.04); border-left: 3px solid #6366f1;
                         padding: 1rem; border-radius: 0 8px 8px 0; margin-bottom: 1rem;
                         line-height: 1.7;'>
                {testo.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)

    # Export testo
    testo_completo = f"RELAZIONE SULLA GESTIONE — {azienda} — Esercizio {anno}\n"
    testo_completo += f"Generata da NEXUS Finance AI Analyst il {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    testo_completo += "=" * 70 + "\n\n"
    for titolo, testo in relazione["sezioni"].items():
        testo_completo += f"{titolo}\n{'-' * 50}\n{testo}\n\n"

    st.download_button("📥 Scarica Relazione (TXT)", testo_completo,
                      f"Relazione_{azienda.replace(' ','_')}_{anno}.txt", "text/plain",
                      use_container_width=True)


def _tab_upload_ai():
    template = """campo,valore
azienda,La Mia SRL
anno,2024
fatturato,3000000
ebitda,350000
ebit,280000
utile_netto,180000
patrimonio_netto,1200000
totale_debiti,2500000
liquidita,120000
interessi_passivi,85000
giorni_incasso_clienti,65
giorni_pagamento_fornitori,40
investimenti_capex,80000
dipendenti,45
zscore,2.1
"""
    st.download_button("📥 Template CSV AI Analyst", template,
                      "template_ai_analyst.csv", "text/csv", use_container_width=True)

    uploaded = st.file_uploader("📂 Carica CSV o Excel bilancio",
                                type=["csv", "xlsx", "xls"], key="ai_upload")
    if uploaded:
        dati = parse_csv_ai(uploaded)
        if dati:
            with st.spinner("🤖 AI Analyst sta elaborando la relazione..."):
                relazione = genera_relazione_gestione(dati)
            _mostra_relazione(relazione)
        else:
            st.error("❌ File non riconosciuto. Usa il template CSV.")


def _tab_manuale_ai():
    with st.form("ai_form"):
        col1, col2 = st.columns(2)
        with col1:
            azienda  = st.text_input("🏢 Nome azienda", "La Mia SRL")
            anno     = st.number_input("Anno esercizio", value=2024, min_value=2000, max_value=2030, step=1)
            fatturato= st.number_input("Fatturato / Ricavi netti (€)", value=3000000.0, step=100000.0)
            ebitda   = st.number_input("EBITDA (€)", value=350000.0, step=10000.0)
            utile    = st.number_input("Utile netto (€)", value=180000.0, step=10000.0)
            pn       = st.number_input("Patrimonio netto (€)", value=1200000.0, step=50000.0)
            debiti   = st.number_input("Totale debiti (€)", value=2500000.0, step=100000.0)
        with col2:
            liquidita= st.number_input("Liquidità disponibile (€)", value=120000.0, step=10000.0)
            interessi= st.number_input("Interessi passivi (€)", value=85000.0, step=1000.0, min_value=0.0)
            dso      = st.number_input("DSO — Giorni incasso clienti", value=65.0, step=1.0, min_value=0.0)
            dpo      = st.number_input("DPO — Giorni pagamento fornitori", value=40.0, step=1.0, min_value=0.0)
            capex    = st.number_input("CAPEX — Investimenti (€)", value=80000.0, step=5000.0)
            dipendenti=st.number_input("N° dipendenti", value=45.0, step=1.0, min_value=0.0)
            zscore   = st.number_input("Z-Score Altman (opz.)", value=2.1, step=0.01,
                                       help="Lascia 0 se non calcolato")

        submitted = st.form_submit_button("🤖 Genera Relazione AI", use_container_width=True, type="primary")

    if submitted:
        dati = {
            "azienda": azienda, "anno": int(anno),
            "fatturato": fatturato, "ebitda": ebitda, "utile_netto": utile,
            "patrimonio_netto": pn, "totale_debiti": debiti, "liquidita": liquidita,
            "interessi_passivi": interessi, "giorni_incasso_clienti": dso,
            "giorni_pagamento_fornitori": dpo, "investimenti_capex": capex,
            "dipendenti": int(dipendenti), "zscore": zscore if zscore != 0 else None,
        }
        with st.spinner("🤖 AI Analyst sta elaborando la relazione..."):
            relazione = genera_relazione_gestione(dati)
        _mostra_relazione(relazione)
