"""
NEXUS — Pagina Contatti (pubblica). Per pilot, white-label e supporto.
"""
import streamlit as st
from utils.ui_kit import page_header, chip_row


def render_contact():
    page_header(
        kicker="Nexus · Parliamone",
        title="Contatti",
        highlight=".",
        subtitle="Pilot gratuito, white-label per studi e banche, supporto tecnico: scrivici.",
    )

    chip_row([
        {"text": "Risposta entro 24h lavorative", "color": "green"},
        {"text": "Italiano / English", "color": "blue"},
    ])
    st.markdown("")

    c1, c2 = st.columns([1.2, 1])

    with c1:
        st.markdown("### ✉️ Scrivici")
        nome = st.text_input("Nome e cognome", placeholder="Maria Rossi", key="ct_nome")
        email = st.text_input("Email", placeholder="maria@azienda.it", key="ct_email")
        motivo = st.selectbox(
            "Motivo",
            ["Voglio entrare nel Pilot gratuito",
             "Sono uno studio commercialista — white-label",
             "Sono una banca — partnership",
             "Supporto tecnico",
             "Privacy / GDPR (privacy@nexus-finance.it)"],
            key="ct_motivo")
        msg = st.text_area("Messaggio", placeholder="Raccontaci in 2 righe la tua realtà…",
                           height=120, key="ct_msg")

        if st.button("Invia richiesta →", type="primary", use_container_width=True):
            if not nome.strip() or "@" not in email or not msg.strip():
                st.error("Compila nome, email valida e messaggio.")
            else:
                # Mailto: nessun backend di invio — apre il client di posta precompilato
                import urllib.parse
                oggetto = f"NEXUS — {motivo} — {nome}"
                corpo = f"Nome: {nome}\nEmail: {email}\nMotivo: {motivo}\n\n{msg}"
                link = ("mailto:info@nexus-finance.it?subject="
                        + urllib.parse.quote(oggetto)
                        + "&body=" + urllib.parse.quote(corpo))
                st.markdown(f"""
                <meta http-equiv="refresh" content="0;url={link}">
                """, unsafe_allow_html=True)
                st.success(f"✅ Grazie {nome.split()[0]}! Si apre il tuo client di posta con la "
                           "richiesta precompilata — premi Invia per spedirla.")
                st.markdown(f"[Se non si apre, clicca qui]({link})")

    with c2:
        st.markdown("### 📬 Recapiti diretti")
        st.markdown("""
        - **Info & Pilot** — info@nexus-finance.it
        - **Privacy & GDPR** — privacy@nexus-finance.it
        - **Risposta entro** — 24h lavorative
        """)
        st.markdown("### 🚀 Perché il Pilot?")
        st.markdown("""
        Selezioniamo i primi clienti e usiamo il loro feedback per rendere NEXUS
        imbattibile rispetto a Legis e agli altri tool di settore. In cambio:
        **tutto gratis** e supporto diretto con il team di sviluppo.
        """)


def render_public_contact():
    render_contact()
    if st.button("← Torna al login / registrazione", type="primary"):
        st.session_state["current_page"] = "credit_readiness"
        st.rerun()
