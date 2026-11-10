"""
NEXUS — Privacy Policy, GDPR e Termini (pagina pubblica).
Redatta secondo il Regolamento UE 2016/679 (GDPR), artt. 13-14.
"""
import streamlit as st
from utils.ui_kit import page_header, chip_row


def render_privacy():
    page_header(
        kicker="Nexus · Trasparenza",
        title="Privacy",
        highlight="& GDPR",
        subtitle="Come trattiamo i tuoi dati: minimizzazione, server in UE, nessuna cessione a terzi.",
    )

    chip_row([
        {"text": "Regolamento UE 2016/679", "color": "blue"},
        {"text": "Dati su Supabase (UE)", "color": "green"},
        {"text": "Nessuna vendita dati", "color": "amber"},
    ])
    st.markdown("")

    st.markdown("""
    ### 1 · Titolare del trattamento

    **Irina Kopitova** — titolare del servizio NEXUS Finance Pro.
    Contatto per esercitare i tuoi diritti: **privacy@nexus-finance.it** (risposta entro 30 giorni).

    ### 2 · Quali dati raccogliamo

    | Categoria | Dati | Finalità | Conservazione |
    |---|---|---|---|
    | **Account** | email, nome, azienda | autenticazione e saluto personalizzato | fino alla cancellazione dell'account |
    | **Analisi** | dati di bilancio caricati (CSV/Excel) e risultati | fornirti le analisi e lo storico | fino alla cancellazione |
    | **Tecnici** | log minimi di servizio | sicurezza e funzionamento | 12 mesi |

    **Principio di minimizzazione**: NEXUS non richiede dati personali non necessari al servizio.
    I file di bilancio restano **di proprietà dell'utente** e non vengono usati per addestrare modelli.

    ### 3 · Dove e come i dati sono conservati

    - **Supabase** (PostgreSQL + Auth) — infrastruttura cloud con datacenter ** nell'Unione Europea **.
    - Accesso protetto da Row Level Security (RLS): ogni utente vede **solo i propri** dati.
    - Le password sono gestite dal sistema di autenticazione Supabase (hash bcrypt, mai in chiaro).
    - Nessun dato di bilancio viene condiviso con terzi, né venduto, né usato per profilazione.

    ### 4 · I tuoi diritti (GDPR)

    In qualsiasi momento puoi richiedere a **privacy@nexus-finance.it**:

    - **Art. 15** — accesso ai tuoi dati
    - **Art. 16** — rettifica (correzione di dati inesatti)
    - **Art. 17** — cancellazione ("diritto all'oblio")
    - **Art. 18** — limitazione del trattamento
    - **Art. 20** — portabilità (export dei tuoi dati in formato leggibile)
    - **Art. 21** — opposizione al trattamento

    La cancellazione dell'account comporta l'eliminazione di profilo e storico associato.

    ### 5 · Cookie e sessione

    NEXUS usa solo il **cookie tecnico di sessione** di Streamlit (necessario al funzionamento)
    e i token di autenticazione Supabase. **Nessun cookie di tracciamento, analytics o pubblicità.**

    ### 6 · Sicurezza

    - Trasmissione cifrata **HTTPS/TLS**
    - Autenticazione con token JWT a scadenza
    - Row Level Security a livello database
    - Rotazione periodica delle chiavi di servizio

    ### 7 · Termini di servizio (sintesi)

    - Il servizio è fornito "così com'è" durante la fase pilot; le analisi sono **supporti
      decisionali e non sostituiscono la valutazione di un professionista abilitato**
      (commercialista, consulente creditizio).
    - L'utente è responsabile della veridicità dei dati caricati.
    - Nessuna garanzia di risultato finanziario o di ottenimento del credito.
    - Puoi interrompere l'uso del servizio in qualsiasi momento.
    """)


def render_public_privacy():
    render_privacy()
    if st.button("← Torna al login / registrazione", type="primary"):
        st.session_state["current_page"] = "credit_readiness"
        st.rerun()
