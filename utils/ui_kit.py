"""
NEXUS Aurora — Design System UI
Ispirazione: SaaS AI-native di nuova generazione (leggero, tipografico, un solo accento).
Componenti: inject_global_css, page_header, kpi_row, pill, mono_label, chip_row,
            empty_state, action_card, feature_grid.
v6.0 — 2026
"""
import html as _html
import streamlit as st

# ── Palette ────────────────────────────────────────────────────────────────────
INK = "#0B1230"          # navy quasi nero — testi forti
MUTED = "#5A6478"        # grigio-blu — testi secondari
ACCENT = "#1E376C"       # blu elettrico — unico accento
ACCENT_2 = "#4A6FA5"     # steel navy — solo per gradienti
VIOLET = "#7C3AED"       # viola — solo per gradienti
SURFACE = "#FFFFFF"
BORDER = "#E6EAF2"
BG = "#F7F9FC"
GREEN = "#16A34A"
AMBER = "#D97706"
RED = "#DC2626"


def _esc(text) -> str:
    return _html.escape(str(text))


# ── CSS globale ────────────────────────────────────────────────────────────────
_CSS = """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,500;0,600;0,700;0,800;1,600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
    /* ─── Variabili ─── */
    :root {
        --nx-ink: #0B1230; --nx-muted: #5A6478; --nx-accent: #1E376C;
        --nx-surface: #FFFFFF; --nx-border: #E6EAF2; --nx-bg: #F6F8F6;
        --nx-green: #16A34A; --nx-amber: #D97706; --nx-red: #DC2626;
        --nx-radius: 18px;
        --nx-font: 'Inter', 'Source Sans Pro', sans-serif;
        --nx-display: 'Playfair Display', Georgia, serif;
        --nx-mono: 'IBM Plex Mono', 'Source Code Pro', monospace;
    }

    /* ─── Base + aurora ─── */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
    [data-testid="stAppViewContainer"] > .main, section.main > div.block-container {
        background: transparent !important;
        font-family: var(--nx-font) !important;
        color: var(--nx-ink) !important;
    }
    [data-testid="stApp"] {
        background:
            radial-gradient(1100px 480px at 88% -8%, rgba(30,55,108,0.10), transparent 60%),
            radial-gradient(800px 420px at -12% 22%, rgba(233,241,235,0.85), transparent 55%),
            radial-gradient(700px 380px at 55% 110%, rgba(201,162,39,0.07), transparent 60%),
            var(--nx-bg) !important;
    }
    [data-testid="stHeader"] {
        background: transparent !important;
        -webkit-backdrop-filter: none; backdrop-filter: none;
    }
    h1, h2, h3, h4 { font-family: var(--nx-display) !important; color: var(--nx-ink) !important; letter-spacing: -0.02em; }
    p, li, span, label { font-family: var(--nx-font); }
    a { color: var(--nx-accent) !important; }
    hr { border-color: var(--nx-border) !important; }

    /* ─── Scrollbar ─── */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-thumb { background: #C7D0E0; border-radius: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }

    /* ─── Sidebar navy ─── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #14264D 0%, #1E376C 58%, #26477E 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    [data-testid="stSidebar"] * { color: #E8EDFB !important; font-family: var(--nx-font); }
    [data-testid="stSidebar"] .stMarkdown hr { border-color: rgba(255,255,255,0.10) !important; }
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.09);
        color: #E8EDFB !important;
        border-radius: 12px;
        padding: 7px 14px;
        font-size: 0.88rem;
        font-weight: 500;
        width: 100%;
        text-align: left;
        transition: all .18s ease;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.12);
        border-color: rgba(255,255,255,0.22);
        transform: translateX(2px);
    }
    .nx-side-label {
        font-family: var(--nx-mono) !important;
        font-size: 0.62rem !important;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: rgba(232,237,251,0.45) !important;
        font-weight: 500;
        margin: 14px 0 4px 2px;
    }
    .nx-side-brand {
        font-family: var(--nx-display) !important;
        font-weight: 700 !important;
        font-size: 1.35rem !important;
        letter-spacing: -0.01em;
    }
    .nx-side-tag {
        font-family: var(--nx-mono) !important;
        font-size: 0.58rem !important;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: rgba(232,237,251,0.5) !important;
    }
    .nx-side-user {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 14px; padding: 10px 12px; margin: 8px 0 4px 0;
    }
    .nx-side-footer {
        text-align: center;
        font-family: var(--nx-mono) !important;
        font-size: 0.58rem !important;
        letter-spacing: 0.14em;
        color: rgba(232,237,251,0.38) !important;
        margin-top: 14px;
        text-transform: uppercase;
    }

    /* ─── Bottoni pill ─── */
    .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
        border-radius: 999px !important;
        border: 1px solid var(--nx-border) !important;
        font-weight: 600 !important;
        font-family: var(--nx-font) !important;
        transition: all .18s ease !important;
        padding: 6px 18px !important;
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(11,18,48,0.10); }
    .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"],
    button[kind="primary"] {
        background: linear-gradient(135deg, #1E376C 0%, #2E4E8F 100%) !important;
        border: none !important;
        color: #fff !important;
        box-shadow: 0 8px 22px rgba(30,55,108,0.28);
    }

    /* ─── Input ─── */
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input {
        border-radius: 12px !important;
        border: 1px solid var(--nx-border) !important;
        font-family: var(--nx-font) !important;
    }
    [data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
        border-color: var(--nx-accent) !important;
        box-shadow: 0 0 0 3px rgba(30,55,108,0.12) !important;
    }

    /* ─── File uploader ─── */
    [data-testid="stFileUploaderDropzone"] {
        border-radius: var(--nx-radius) !important;
        border: 1.5px dashed #B9C6E2 !important;
        background: #FFFFFF !important;
    }

    /* ─── Metriche Streamlit (tutte le pagine) ─── */
    [data-testid="stMetric"], [data-testid="metric-container"] {
        background: var(--nx-surface);
        border: 1px solid var(--nx-border);
        border-radius: var(--nx-radius);
        padding: 16px 18px;
        box-shadow: 0 1px 3px rgba(11,18,48,0.04);
    }
    [data-testid="stMetricLabel"] p, [data-testid="metric-container"] label {
        color: var(--nx-muted) !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
    }
    [data-testid="stMetricValue"], [data-testid="metric-container"] > div {
        color: var(--nx-ink) !important;
        font-family: var(--nx-display) !important;
        font-weight: 700 !important;
    }

    /* ─── Tabs ─── */
    [data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--nx-border); }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 999px 999px 0 0;
        padding: 8px 18px;
        font-weight: 600;
        color: var(--nx-muted) !important;
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        color: var(--nx-accent) !important;
        background: rgba(30,55,108,0.06);
    }
    [data-testid="stTabs"] button[data-baseweb="tab"] svg { display: none; }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"] { background: var(--nx-accent) !important; }

    /* ─── Expander / alert / dataframe ─── */
    [data-testid="stExpander"] details {
        border: 1px solid var(--nx-border) !important;
        border-radius: var(--nx-radius) !important;
        background: var(--nx-surface) !important;
    }
    [data-testid="stAlert"] { border-radius: 14px !important; border: 1px solid var(--nx-border); }
    [data-testid="stDataFrame"] { border-radius: var(--nx-radius) !important; border: 1px solid var(--nx-border) !important; }

    /* ─── Chat Copilot ─── */
    [data-testid="stChatMessage"] {
        background: var(--nx-surface) !important;
        border: 1px solid var(--nx-border) !important;
        border-radius: var(--nx-radius) !important;
        padding: 14px 16px !important;
    }
    [data-testid="stChatInput"] textarea, [data-testid="stChatInput"] > div {
        border-radius: 999px !important;
        border: 1.5px solid #B9C6E2 !important;
        background: #fff !important;
    }

    /* ─── Componenti Aurora ─── */
    .nx-kicker {
        font-family: var(--nx-mono);
        font-size: 0.66rem; font-weight: 600;
        letter-spacing: 0.22em; text-transform: uppercase;
        color: #B98A2F;
        margin-bottom: 6px;
    }
    .nx-h1 {
        font-family: var(--nx-display);
        font-size: clamp(1.7rem, 3.2vw, 2.5rem);
        font-weight: 700; line-height: 1.08;
        color: var(--nx-ink); margin: 0;
        letter-spacing: -0.03em;
    }
    .nx-grad {
        background: linear-gradient(120deg, #1E376C 0%, #0034A4 48%, #B98A2F 100%);
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent; color: transparent;
    }
    .nx-sub { color: var(--nx-muted); font-size: 1.0rem; margin: 8px 0 0 0; }
    .nx-hero { padding: 6px 0 18px 0; }

    .nx-kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
        gap: 14px; margin: 6px 0 14px 0;
    }
    .nx-kpi {
        background: var(--nx-surface);
        border: 1px solid var(--nx-border);
        border-radius: var(--nx-radius);
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(11,18,48,0.04);
        transition: all .2s ease;
    }
    .nx-kpi:hover { transform: translateY(-2px); box-shadow: 0 10px 28px rgba(11,18,48,0.08); }
    .nx-kpi-kicker {
        font-family: var(--nx-mono); font-size: 0.6rem; font-weight: 600;
        letter-spacing: 0.18em; text-transform: uppercase; color: var(--nx-muted);
        margin-bottom: 8px;
    }
    .nx-kpi-value {
        font-family: var(--nx-display); font-weight: 700;
        font-size: 1.75rem; line-height: 1; color: var(--nx-ink);
        letter-spacing: -0.02em;
    }
    .nx-kpi-value.blue { color: var(--nx-accent); }
    .nx-kpi-value.green { color: var(--nx-green); }
    .nx-kpi-value.red { color: var(--nx-red); }
    .nx-kpi-value.amber { color: var(--nx-amber); }
    .nx-kpi-sub { font-size: 0.8rem; color: var(--nx-muted); margin-top: 6px; line-height: 1.35; }

    .nx-card {
        background: var(--nx-surface);
        border: 1px solid var(--nx-border);
        border-radius: var(--nx-radius);
        padding: 18px 22px;
        box-shadow: 0 1px 3px rgba(11,18,48,0.04);
    }
    .nx-card-title { font-weight: 700; font-size: 1.02rem; color: var(--nx-ink); }

    .nx-chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 2px 0; }
    .nx-chip {
        display: inline-flex; align-items: center; gap: 6px;
        border: 1px solid var(--nx-border);
        background: var(--nx-surface);
        border-radius: 999px;
        padding: 5px 14px;
        font-size: 0.8rem; font-weight: 600; color: var(--nx-ink);
    }
    .nx-chip .dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
    .dot.blue { background: var(--nx-accent); } .dot.green { background: var(--nx-green); }
    .dot.amber { background: var(--nx-amber); } .dot.red { background: var(--nx-red); }
    .dot.violet { background: var(--nx-violet, #7C3AED); }

    .nx-pill {
        display: inline-block; border-radius: 999px;
        padding: 4px 12px; font-size: 0.72rem; font-weight: 700;
        letter-spacing: 0.04em;
    }
    .nx-pill.green { background: #DCFCE7; color: #166534; }
    .nx-pill.amber { background: #FEF3C7; color: #92400E; }
    .nx-pill.red   { background: #FEE2E2; color: #991B1B; }
    .nx-pill.blue  { background: #E3E9F4; color: #1E376C; }
    .nx-pill.grey  { background: #EEF2F7; color: #475569; }

    .nx-empty {
        text-align: center; padding: 34px 20px;
        border: 1.5px dashed #C7D0E0; border-radius: var(--nx-radius);
        background: rgba(255,255,255,0.65);
    }
    .nx-empty .ico { font-size: 2rem; }
    .nx-empty .t { font-family: var(--nx-display); font-weight: 700; font-size: 1.1rem; margin-top: 8px; color: var(--nx-ink); }
    .nx-empty .d { color: var(--nx-muted); font-size: 0.88rem; margin-top: 4px; }

    .nx-feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 10px; margin-top: 8px;
    }
    .nx-feature {
        background: var(--nx-surface); border: 1px solid var(--nx-border);
        border-radius: 14px; padding: 12px 14px;
        font-size: 0.84rem; color: var(--nx-ink); font-weight: 500;
        display: flex; gap: 8px; align-items: flex-start; line-height: 1.4;
    }

    .nx-action {
        background: var(--nx-surface); border: 1px solid var(--nx-border);
        border-left: 4px solid var(--nx-accent);
        border-radius: 14px; padding: 14px 18px; margin-bottom: 10px;
    }
    .nx-action .t { font-weight: 700; color: var(--nx-ink); }
    .nx-action .d { color: var(--nx-muted); font-size: 0.85rem; margin-top: 3px; }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stStatusWidget"] { visibility: hidden; }
    /* Compatibilità hero scuri definiti nelle pagine (es. credit_readiness) */
    .cr-hero h1, .cr-hero h2, .cr-hero h3, .cr-hero p { color: #FFFFFF !important; }
    .cr-hero p { color: #94a3b8 !important; }
    </style>
"""


def inject_global_css():
    """Inietta il design system Aurora. Da chiamare UNA volta in app.py.
    Nota: le righe vuote vengono rimosse — in Markdown interrompono il blocco HTML."""
    css = "\n".join(l for l in _CSS.splitlines() if l.strip())
    st.markdown(css, unsafe_allow_html=True)


# ── Componenti Python → HTML ──────────────────────────────────────────────────
def mono_label(text: str, color: str = ""):
    style = f" style='color:{color} !important;'" if color else ""
    st.markdown(f"<div class='nx-side-label'{style}>{_esc(text)}</div>", unsafe_allow_html=True)


def page_header(kicker: str, title: str, highlight: str = "", subtitle: str = ""):
    """Header tipografico Aurora: kicker mono + titolo display con parola evidenziata."""
    hi = f" <span class='nx-grad'>{_esc(highlight)}</span>" if highlight else ""
    sub = f"<p class='nx-sub'>{_esc(subtitle)}</p>" if subtitle else ""
    st.markdown(
        f"<div class='nx-hero'><div class='nx-kicker'>{_esc(kicker)}</div>"
        f"<h1 class='nx-h1'>{_esc(title)}{hi}</h1>{sub}</div>",
        unsafe_allow_html=True,
    )


def kpi_row(items: list):
    """Riga di KPI in stile 'risultati quantificati'.
    items: [{label, value, sub, tone}] — tone: blue|green|red|amber|'' """
    cells = []
    for i, it in enumerate(items, 1):
        tone = it.get("tone", "")
        cls = f" {tone}" if tone else ""
        sub = f"<div class='nx-kpi-sub'>{_esc(it['sub'])}</div>" if it.get("sub") else ""
        cells.append(
            f"<div class='nx-kpi'><div class='nx-kpi-kicker'>"
            f"{i:02d} · {_esc(it['label'])}</div>"
            f"<div class='nx-kpi-value{cls}'>{_esc(it['value'])}</div>{sub}</div>"
        )
    st.markdown(f"<div class='nx-kpi-grid'>{''.join(cells)}</div>", unsafe_allow_html=True)


def pill(text: str, tone: str = "grey") -> str:
    """Pill HTML da incorporare in altri markdown. tone: green|amber|red|blue|grey"""
    return f"<span class='nx-pill {tone}'>{_esc(text)}</span>"


def chip_row(chips: list):
    """chips: [{text, color}] — color: blue|green|amber|red|violet"""
    parts = []
    for c in chips:
        color = c.get("color", "blue")
        parts.append(f"<span class='nx-chip'><span class='dot {color}'></span>{_esc(c['text'])}</span>")
    st.markdown(f"<div class='nx-chip-row'>{''.join(parts)}</div>", unsafe_allow_html=True)


def empty_state(icon: str, title: str, description: str):
    st.markdown(
        f"<div class='nx-empty'><div class='ico'>{icon}</div>"
        f"<div class='t'>{_esc(title)}</div><div class='d'>{_esc(description)}</div></div>",
        unsafe_allow_html=True,
    )


def action_card(title: str, description: str, color: str = ACCENT):
    st.markdown(
        f"<div class='nx-action' style='border-left-color:{color};'>"
        f"<div class='t'>{_esc(title)}</div><div class='d'>{_esc(description)}</div></div>",
        unsafe_allow_html=True,
    )


def feature_grid(features: list):
    """features: [{icon, text}]"""
    cells = [f"<div class='nx-feature'><span>{f.get('icon','✓')}</span><span>{_esc(f['text'])}</span></div>"
             for f in features]
    st.markdown(f"<div class='nx-feature-grid'>{''.join(cells)}</div>", unsafe_allow_html=True)
