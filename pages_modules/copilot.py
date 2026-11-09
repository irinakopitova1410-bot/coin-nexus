"""
NEXUS Copilot — Il centro di comando AI-native.
L'utente chiede in linguaggio naturale → il Copilot esegue l'analisi sui dati
già caricati (nessuna API esterna: motore regole + motore finanziario locale).
v6.0 Aurora
"""
import re
import streamlit as st
from utils.ui_kit import page_header, chip_row, kpi_row, pill, empty_state, mono_label


# ── Motore di intent (regole, italiano) ───────────────────────────────────────
INTENTS = [
    ("readiness",    "Credit Readiness",     ["credito", "banca", "readiness", "finanziab", "ottenere credito", "fido", "prestito", "mutuo"]),
    ("risk_analysis","Z-Score Altman",       ["z-score", "zscore", "altman", "zona di rischio", "fallimentare", "insolvenza statistica"]),
    ("whatif_simulator", "What-If Simulator",["simula", "scenario", "what-if", "what if", "e se", "ipotizzo"]),
    ("cashflow",     "Cash Flow",            ["cash flow", "flusso", "liquidit", "tesoreria", "ccn", "circolante"]),
    ("early_warning","Early Warning CCII",   ["crisi", "ccii", "allerta", "early warning", "dscr", "inso"]),
    ("esg_scoring",  "ESG Scoring",          ["esg", "sostenib", "ambientale", "green", "esg score"]),
    ("audit_report", "Audit Report ISA 320", ["audit", "isa", "revisione"]),
    ("credit_scoring","Credit Scoring",      ["rating", "credit scoring", "score di credito", "merito"]),
    ("ratio_analysis","Ratio Analysis",      ["ratio", "indici", "rotazione", "dso", "dpo", "margine"]),
    ("variance_analysis","Variance Analysis",["varianza", "variance", "budget", "consuntivo", "scostamento"]),
    ("open_banking", "Open Banking PSD2",    ["open banking", "psd2", "conto bancario", "movimenti"]),
    ("erp_import",   "Import da ERP",        ["carica", "import", "csv", "excel", "bilancio", "erp", "sap", "zucchetti", "teamsystem"]),
    ("history",      "Storico Analisi",      ["storico", "cronologia", "precedenti", "vecchie analisi"]),
]

SUGGESTIONS = [
    "Come sta la mia azienda?",
    "Come ottengo più credito dalla banca?",
    "Che rischio di crisi ho?",
    "Simula +10% ricavi",
]


# ── Motore finanziario locale ─────────────────────────────────────────────────
def _f(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _altman(d: dict):
    """Z-Score Altman standard su dati ERP (dizionario REQUIRED_FIELDS)."""
    ta = _f(d.get("total_assets"))
    if ta <= 0:
        return None
    wc = _f(d.get("working_capital"))
    re_ = _f(d.get("retained_earnings"))
    ebit = _f(d.get("ebit"))
    eq = _f(d.get("equity"))
    tl = _f(d.get("total_liabilities")) or (ta - eq if eq else 0.0)
    rev = _f(d.get("ricavi_netti") or d.get("revenue"))
    z = (1.2 * wc / ta + 1.4 * re_ / ta + 3.3 * ebit / ta
         + 0.6 * (eq / tl if tl > 0 else 0.0)
         + 1.0 * (rev / ta if rev else 0.0))
    return z


def _zona(z: float):
    if z > 2.99:
        return "Safe", "green"
    if z >= 1.81:
        return "Grey Zone", "amber"
    return "Distress", "red"


def _eur(v: float) -> str:
    neg = v < 0
    s = f"{abs(v):,.0f}".replace(",", ".")
    return ("-€ " if neg else "€ ") + s


def _company_snapshot() -> str:
    """Mini report esecutivo dai dati ERP in sessione."""
    d = st.session_state.get("erp_data") or {}
    if not d:
        return ""
    z = _altman(d)
    lines = []
    if z is not None:
        zona, tone = _zona(z)
        if tone == "red":
            msg = "Sovraccarico finanziario severo: servono interventi strutturali immediati."
        elif tone == "amber":
            msg = "Equilibrio fragile: monitorare e agire sulle leve operative."
        else:
            msg = "Equilibrio solido: potenziale di crescita creditizia."
        lines.append(f"**Z-Score Altman: {z:.2f}** — zona {pill(zona, tone)}. {msg}")
    ebitda = _f(d.get("ebitda"))
    rev = _f(d.get("ricavi_netti") or d.get("revenue"))
    if rev and ebitda:
        lines.append(f"**EBITDA Margin: {ebitda / rev * 100:.1f}%** su ricavi {_eur(rev)}.")
    ta = _f(d.get("total_assets"))
    eq = _f(d.get("equity"))
    if ta and eq:
        lines.append(f"**Patrimonio netto / Attivo: {eq / ta * 100:.1f}%** — leva finanziaria "
                     f"{'molto alta, attenzione agli interessi' if eq / ta < 0.10 else 'nella norma'}.")
    inv = _f(d.get("inventory"))
    ap = _f(d.get("accounts_payable"))
    if inv and ap and rev:
        dpo = ap / (0.6 * rev) * 365 if rev else 0
        lines.append(f"**DPO stimato: {dpo:.0f} giorni** — giorni di pagamento ai fornitori.")
    return "\n\n".join(lines)


def _azioni_creditizie(d: dict) -> str:
    """Top azioni per sbloccare credito — regole su dati reali."""
    azioni = []
    eq = _f(d.get("equity"))
    ta = _f(d.get("total_assets"))
    ebitda = _f(d.get("ebitda"))
    interests = _f(d.get("interest_expense"))
    if ta and eq and eq / ta < 0.15:
        azioni.append("**Ricapitalizzazione**: il patrimonio netto pesa meno del 15% dell'attivo — "
                      "convertire debito in capitale o apportare riserve rafforza ogni rating.")
    if interests and ebitda and ebitda / interests < 3:
        azioni.append("**Rinegoziazione dell'onere finanziario**: EBITDA < 3× interessi — "
                      "allungare le scadenze e rinegoziare il tasso riporta il DSCR sopra 1,2×.")
    inv = _f(d.get("inventory"))
    rev = _f(d.get("ricavi_netti") or d.get("revenue"))
    if inv and rev and inv / rev > 0.25:
        azioni.append("**Snellimento rimanenze**: le scorte superano il 25% dei ricavi — "
                      "scontare il giacenzario libera cassa immediata.")
    if not azioni:
        azioni.append("**Mantieni i profili**: gli indicatori chiave sono in linea — "
                      "usa lo storico per documentare la tendenza alla banca.")
    return "\n\n".join(f"- {a}" for a in azioni)


# ── Risposta del Copilot ──────────────────────────────────────────────────────
def _respond(q: str):
    """Ritorna (risposta_markdown, pagina_da_aprire|None)."""
    ql = q.lower()
    has_data = bool(st.session_state.get("erp_data"))

    # 1) Capabilities / help
    if any(k in ql for k in ["chi sei", "cosa sai fare", "aiuto", "help", "ciao", "come funzioni"]):
        return (
            "Sono **NEXUS Copilot**, il tuo analista finanziario AI. Leggo il bilancio caricato "
            "e rispondo con numeri, non con promesse.\n\n"
            "**Cosa posso fare ora:**\n- leggere lo stato di salute (Z-Score, margini, leva)\n"
            "- dirti come sbloccare credito bancario\n- stimare il rischio di crisi (CCII)\n"
            "- instradarti all'analisi giusta con i dati già caricati\n\n"
            "Prova: _\"come sta la mia azienda?\"_ oppure _\"come ottengo più credito?\"_",
            None,
        )

    # 2) Stato azienda / diagnosi
    if any(k in ql for k in ["come sta", "situazione", "salute", "diagnosi", "riassum", "panoramica", "come va"]):
        if not has_data:
            return ("Non ho ancora un bilancio da leggere. Caricalo e in 10 secondi ti do "
                    "Z-Score, margini e leve d'azione.", "credit_readiness")
        snap = _company_snapshot()
        return (f"Ecco il quadro dal bilancio caricato:\n\n{snap}\n\n"
                "Vuoi il dettaglio? Aprilo in un click sotto.", "dashboard")

    # 3) Credito / banca
    if any(k in ql for k in ["credito", "banca", "finanziam", "fido", "prestito", "mutuo", "readiness"]):
        if not has_data:
            return ("Per calcolare quanto credito puoi ottenere serve il bilancio. "
                    "Caricalo qui:", "credit_readiness")
        return ("**Come sbloccare credito ora** — leve ordinate per impatto sul rating:\n\n"
                f"{_azioni_creditizie(st.session_state['erp_data'])}\n\n"
                "Il punteggio completo e il piano d'azione sono qui:", "credit_readiness")

    # 4) Crisi / CCII
    if any(k in ql for k in ["crisi", "ccii", "allerta", "insolvenz", "rischio di crisi"]):
        return ("Il monitoraggio CCII valuta 5 indici di crisi su squilibri patrimoniali, "
                "reddituali e finanziari. Esegui il check qui:", "early_warning")

    # 5) Simulazioni
    if any(k in ql for k in ["simula", "scenario", "what-if", "what if", "e se"]):
        return ("Nel What-If Simulator muovi ricavi, costi e margini e vedi l'effetto "
                "immediato su Z-Score, probabilità di default e covenant.", "whatif_simulator")

    # 6) Cash flow
    if any(k in ql for k in ["cash", "flusso", "liquidit", "tesoreria", "circolante"]):
        return ("L'analisi Cash Flow ricostruisce operativa, investimenti e finanziamento "
                "con proiezioni a 5 anni.", "cashflow")

    # 7) Intent per pagina (parole chiave)
    for page_id, label, keywords in INTENTS:
        if any(k in ql for k in keywords):
            return (f"Perfetto — apro **{label}**. Se hai già caricato il bilancio "
                    "userò quei dati, altrimenti ti guido io al caricamento.", page_id)

    # 8) Fallback: diagnosi se ci sono dati, altrimenti guida
    if has_data:
        snap = _company_snapshot()
        return ("Interpretazione della domanda sulla situazione attuale:\n\n"
                f"{snap}\n\nPuoi anche chiedermi: _\"come ottengo più credito?\"_, "
                "_\"che rischio di crisi ho?\"_, _\"simula +10% ricavi\"_.", None)
    return ("Ancora non ho dati su cui lavorare. Carica il bilancio (CSV o Excel) in "
            "**Credit Readiness** e da quel momento ogni mia risposta userà i tuoi numeri reali.",
            "credit_readiness")


# ── Render ────────────────────────────────────────────────────────────────────
def render_copilot(user: dict):
    name = (user.get("full_name") or user.get("email", "")).split()[0] if user else ""

    page_header(
        kicker="Nexus Copilot · AI-Native Command Center",
        title=f"{name}, chiedi." if name else "Chiedi.",
        highlight="Io analizzo.",
        subtitle="Il tuo bilancio, letto da un copilot che risponde con numeri — assessment, azioni e navigazione in un click.",
    )

    chip_row([
        {"text": "Lettura bilancio", "color": "blue"},
        {"text": "Diagnosi Z-Score", "color": "violet"},
        {"text": "Leve di credito", "color": "green"},
        {"text": "Routing analisi", "color": "amber"},
    ])

    # Suggerimenti rapidi
    cols = st.columns(len(SUGGESTIONS))
    for i, s in enumerate(SUGGESTIONS):
        if cols[i].button(s, key=f"sugg_{i}", use_container_width=True):
            msgs = st.session_state.setdefault("copilot_msgs", [])
            msgs.append({"role": "user", "text": s})
            answer, page = _respond(s)
            msgs.append({"role": "assistant", "text": answer, "page": page})
            st.rerun()

    st.markdown("")

    # Storico conversazione
    for i, m in enumerate(st.session_state.get("copilot_msgs", [])):
        with st.chat_message("user" if m["role"] == "user" else "assistant"):
            st.markdown(m["text"], unsafe_allow_html=True)
            if m.get("page"):
                if st.button("Apri →  " + dict(page_map())[m["page"]], key=f"go_{i}",
                             type="primary"):
                    st.session_state["current_page"] = m["page"]
                    st.rerun()

    if not st.session_state.get("copilot_msgs"):
        empty_state(
            "◆",
            "Chiedi in italiano, io faccio il resto",
            "Esempi: «come sta la mia azienda?» · «come ottengo più credito?» · «che rischio di crisi ho?»",
        )

    # Input chat
    prompt = st.chat_input("Scrivi al Copilot… es: «come ottengo più credito?»")
    if prompt:
        msgs = st.session_state.setdefault("copilot_msgs", [])
        msgs.append({"role": "user", "text": prompt})
        answer, page = _respond(prompt)
        msgs.append({"role": "assistant", "text": answer, "page": page})
        st.rerun()


def page_map():
    return {
        "credit_readiness": "Credit Readiness",
        "risk_analysis": "Z-Score Altman",
        "credit_scoring": "Credit Scoring",
        "ratio_analysis": "Ratio Analysis",
        "cashflow": "Cash Flow",
        "audit_report": "Audit Report ISA 320",
        "early_warning": "Early Warning CCII",
        "esg_scoring": "ESG Scoring",
        "ai_analyst": "AI Financial Analyst",
        "open_banking": "Open Banking PSD2",
        "whatif_simulator": "What-If Simulator",
        "variance_analysis": "Variance Analysis",
        "erp_import": "Import da ERP",
        "history": "Storico Analisi",
        "dashboard": "Dashboard",
    }
