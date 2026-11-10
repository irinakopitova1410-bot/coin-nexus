"""
NEXUS — Pagina Prezzi (pubblica, raggiungibile anche pre-login).
Piano pilot gratuito durante la fase di acquisizione clienti.
"""
import streamlit as st
from utils.ui_kit import page_header, chip_row


PLANS = [
    {
        "nome": "Pilot",
        "prezzo": "Gratis",
        "sotto": "Fase di lancio · tempo illimitato",
        "tone": "grey",
        "features": [
            "✅ Tutte le analisi illimitate",
            "✅ Credit Readiness + Z-Score",
            "✅ Copilot AI nativo",
            "✅ Storico cloud delle analisi",
            "✅ Export PDF",
            "— Benchmark di settore avanzati",
            "— Multi-azienda",
        ],
        "cta": None,
    },
    {
        "nome": "Pro",
        "prezzo": "€59",
        "sotto": "per mese · 1 azienda",
        "tone": "blue",
        "evidenzia": True,
        "features": [
            "✅ Tutto il piano Pilot",
            "✅ Benchmark di settore (ATECO)",
            "✅ Early Warning CCII automatico",
            "✅ Report PDF personalizzati col logo",
            "✅ What-If Simulator illimitato",
            "✅ Supporto email prioritario (24h)",
        ],
        "cta": "Richiedi attivazione →",
    },
    {
        "nome": "Business",
        "prezzo": "€149",
        "sotto": "per mese · fino a 10 aziende",
        "tone": "blue",
        "features": [
            "✅ Tutto il piano Pro",
            "✅ Multi-azienda e multi-utente",
            "✅ API REST per il tuo ERP",
            "✅ White-label (il tuo logo e dominio)",
            "✅ Onboarding dedicato (2h)",
            "✅ Supporto prioritario (4h)",
        ],
        "cta": "Contattaci →",
    },
]


def render_pricing():
    page_header(
        kicker="Nexus · Piani e prezzi",
        title="Prezzi",
        highlight="trasparenti.",
        subtitle="Inizia gratis con il piano Pilot. Passa a Pro quando NEXUS ti fa risparmiare tempo e ottiene credito.",
    )

    chip_row([
        {"text": "Nessuna carta richiesta", "color": "green"},
        {"text": "Dati su server UE (Supabase)", "color": "blue"},
        {"text": "Cancellazione in qualsiasi momento", "color": "amber"},
    ])
    st.markdown("")

    cols = st.columns(len(PLANS))
    for i, p in enumerate(PLANS):
        with cols[i]:
            ev = p.get("evidenzia", False)
            border = "2px solid #1E376C" if ev else "1px solid #E6EAF2"
            badge = ("<div style='font-family:IBM Plex Mono,monospace;font-size:0.6rem;"
                     "letter-spacing:0.18em;text-transform:uppercase;color:#fff;"
                     "background:#1E376C;display:inline-block;border-radius:999px;"
                     "padding:3px 10px;margin-bottom:8px;'>Più scelto</div><br>") if ev else ""
            feats = "".join(f"<div style='margin:5px 0;color:#334155;font-size:0.86rem;'>{f}</div>"
                            for f in p["features"])
            st.markdown(f"""
            <div style="background:#fff;border:{border};border-radius:18px;padding:20px 22px;
                        box-shadow:0 10px 34px rgba(11,18,48,{'0.12' if ev else '0.05'});height:100%;">
                {badge}
                <div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;letter-spacing:0.2em;
                            text-transform:uppercase;color:#5A6478;">{p['nome']}</div>
                <div style="font-family:'Playfair Display',serif;font-weight:700;font-size:2.1rem;
                            color:#0B1230;margin:4px 0 0 0;">{p['prezzo']}</div>
                <div style="color:#5A6478;font-size:0.8rem;margin-bottom:12px;">{p['sotto']}</div>
                {feats}
            </div>
            """, unsafe_allow_html=True)

            if p.get("cta"):
                if st.button(p["cta"], use_container_width=True, key=f"plan_{p['nome']}",
                             type="primary" if ev else "secondary"):
                    st.session_state["current_page"] = "contact"
                    st.rerun()
            else:
                if st.button("Inizia ora gratis →", use_container_width=True, key="plan_free"):
                    st.session_state["current_page"] = "login"
                    st.rerun()

    st.divider()
    st.markdown("""
    ### 🔌 White-label per studi commerciali e banche

    NEXUS con il **tuo brand**: logo, colori, dominio (es. `app.tuostudio.it`), report PDF
    personalizzati e pannello clienti. A partire da **€2.500 di setup** + €149/mese.
    Ideale per studi di commercialisti che vogliono offrire analisi finanziaria AI ai propri clienti.

    👉 Descrivi la tua realtà nella pagina **Contatti** e prepariamo una demo dedicata.
    """)

    st.info("💡 **Fase Pilot attiva**: il piano a pagamento non è ancora attivato. "
            "Ogni funzionalità è gratuita per i primi clienti — chiedi in Contatti come entrare nel programma.", icon="🎁")


def render_public_pricing():
    """Versione pubblica pre-login: stessa pagina + bottone torna al login."""
    render_pricing()
    if st.button("← Torna al login / registrazione", type="primary"):
        st.session_state["current_page"] = "credit_readiness"
        st.rerun()
