"""Offline Streamlit route/action regression tests; no real DB or HTTP calls."""
import importlib
import socket
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Network access forbidden in page audit")
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr("requests.sessions.Session.request", forbidden)
    import services.db as db
    import services.auth as auth
    sb = MagicMock()
    sb.table.return_value = sb
    for method in ("select", "order", "limit", "eq"):
        getattr(sb, method).return_value = sb
    sb.execute.return_value.data = []
    sb.execute.return_value.count = 0
    user = {"id": "offline-test", "email": "test@example.invalid", "role": "admin",
            "full_name": "Offline Test", "company_name": "Test", "access_token": "offline"}
    monkeypatch.setattr(auth, "get_current_user", lambda: user)
    monkeypatch.setattr(auth, "is_admin", lambda: True)
    monkeypatch.setattr(auth, "get_supabase", lambda: sb)
    monkeypatch.setattr(db, "get_supabase", lambda: sb)
    monkeypatch.setattr(db, "get_auth_supabase", lambda *a, **k: sb)
    saves = {}
    for name in ("save_risk_analysis", "save_credit_report", "save_audit_report"):
        saves[name] = MagicMock(return_value=True)
        monkeypatch.setattr(db, name, saves[name])
    monkeypatch.setattr(db, "get_recent_analyses", lambda *a, **k: [])
    monkeypatch.setattr(db, "get_all_history", lambda *a, **k: {})
    # Existing test modules may already have imported page-level aliases.
    for module in list(sys.modules.values()):
        if getattr(module, "__name__", "").startswith("pages_modules."):
            for name in (*saves, "get_recent_analyses", "get_all_history", "get_supabase", "get_auth_supabase"):
                if hasattr(module, name):
                    monkeypatch.setattr(module, name, getattr(db, name))
    monkeypatch.delenv("NEXUS_DEV_BYPASS", raising=False)
    return saves


ROUTES = ["credit_readiness", "copilot", "dashboard", "risk_analysis", "credit_scoring",
          "ratio_analysis", "cashflow", "audit_report", "early_warning", "esg_scoring",
          "ai_analyst", "open_banking", "whatif_simulator", "variance_analysis", "erp_import",
          "pricing", "privacy", "contact", "history", "admin_panel"]


def app(route):
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20)
    at.session_state["current_page"] = route
    at.session_state["cached_users"] = []  # Admin list is an HTTP endpoint, not called.
    at.session_state["user"] = {"access_token": "offline"}
    return at.run()


def clean(at):
    assert not at.exception, [e.message for e in at.exception]
    assert not at.error, [e.value for e in at.error]


@pytest.mark.parametrize("route", ROUTES)
def test_all_routes_initial_and_idle_rerun(route, offline):
    at = app(route)
    clean(at)
    clean(at.run())
    assert all(not mock.called for mock in offline.values())


@pytest.mark.parametrize("route,label", [
    ("credit_readiness", "⚡ ANALIZZA CREDIT READINESS"),
    ("credit_scoring", "💳 CALCOLA CREDIT SCORE"),
    ("ratio_analysis", "📊 CALCOLA TUTTI I RATIO"),
    ("audit_report", "📊 GENERA AUDIT REPORT"),
    ("early_warning", "🚨 Calcola Early Warning"),
    ("esg_scoring", "🌿 Calcola ESG Score"),
    ("ai_analyst", "🤖 Genera Relazione AI"),
    ("whatif_simulator", "🔮 Avvia Simulatore"),
])
def test_manual_actions(route, label):
    at = app(route)
    next(b for b in at.button if b.label == label).click().run()
    clean(at)


def test_full_and_crisis_pdf_generation():
    from utils.pdf_export import generate_full_report
    from utils.pdf_crisi_impresa import generate_crisi_impresa_report
    from engine.calculations import altman_z_prime
    from engine.financial_ratios import calculate_all_ratios
    from engine.cashflow import calculate_cashflow
    data = dict(total_assets=1_000_000, equity=400_000, total_liabilities=600_000,
                current_assets=450_000, current_liabilities=200_000, revenue=900_000,
                ebit=100_000, ebitda=130_000, net_income=60_000, depreciation=30_000,
                interest_expense=20_000, total_debt=300_000)
    z = altman_z_prime(250_000, 1_000_000, 50_000, 100_000, 400_000, 600_000, 900_000)
    full = generate_full_report("Società € — 测试", altman_result=z,
                               ratio_result=calculate_all_ratios(data),
                               cashflow_result=calculate_cashflow(data), raw_data=data)
    crisis = generate_crisi_impresa_report("Società € — 测试", data)
    assert full.startswith(b"%PDF") and crisis.startswith(b"%PDF")


def test_credit_save_survives_calculate_rerun_and_passes_token(offline):
    at = app("credit_scoring")
    next(b for b in at.button if b.label == "💳 CALCOLA CREDIT SCORE").click().run()
    assert not offline["save_credit_report"].called
    at.button(key="save_credit").click().run()
    clean(at)
    offline["save_credit_report"].assert_called_once()
    at.run()
    offline["save_credit_report"].assert_called_once()
    # Editing an input invalidates the old calculated result and its save button.
    next(n for n in at.number_input if n.label == "EBIT (€)").set_value(20_000.0).run()
    assert not any(b.key == "save_credit" for b in at.button)


@pytest.mark.parametrize("route,calculate,pdf_key", [
    ("ratio_analysis", "📊 CALCOLA TUTTI I RATIO", "pdf_ratio"),
    ("risk_analysis", "🔍 CALCOLA Z-SCORE", "pdf_btn_manual"),
])
def test_manual_pdf_button_remains_actionable(route, calculate, pdf_key, offline):
    at = app(route)
    if route == "risk_analysis":
        inputs = {"Totale Attivo (€)": 1_000_000.0, "Totale Passivo (€)": 300_000.0,
                  "Patrimonio Netto (€)": 700_000.0, "Ricavi (€)": 2_000_000.0,
                  "EBIT (€)": 400_000.0, "Attivo Corrente (€)": 600_000.0,
                  "Passivo Corrente (€)": 100_000.0, "Riserve / Utili portati (€)": 200_000.0}
        for label, value in inputs.items():
            next(n for n in at.number_input if n.label == label).set_value(value)
    next(b for b in at.button if b.label == calculate).click().run()
    clean(at)
    at.button(key=pdf_key).click().run()
    clean(at)
    assert any("Scarica" in d.label for d in at.get("download_button"))
    assert not offline["save_risk_analysis"].called
    if route == "risk_analysis":
        at.button(key="zscore_save_manual").click().run()
        offline["save_risk_analysis"].assert_called_once()
        at.run()
        offline["save_risk_analysis"].assert_called_once()


@pytest.mark.parametrize("route", ["pricing", "privacy", "contact"])
def test_public_routes_without_login(route, monkeypatch):
    monkeypatch.setattr("services.auth.get_current_user", lambda: None)
    clean(app(route))


def test_esg_less_co2_is_better_and_scores_bounded():
    from pages_modules.esg_scoring import calcola_score_pillar, DOMANDE_E
    low = calcola_score_pillar({"emissioni_co2": 0}, DOMANDE_E)
    high = calcola_score_pillar({"emissioni_co2": 500}, DOMANDE_E)
    assert low["score"] > high["score"]
    outside = calcola_score_pillar({"emissioni_co2": -100}, DOMANDE_E)
    assert all(0 <= row["score"] <= 100 for row in outside["dettaglio"])


def test_uploaded_audit_is_not_saved_on_reruns(monkeypatch, offline):
    import io
    import pages_modules.audit_report as page
    source = io.BytesIO(page.AUDIT_TEMPLATE_CSV.encode())
    source.name = "audit.csv"
    source.size = len(source.getvalue())
    import streamlit as st
    real_uploader = st.file_uploader
    monkeypatch.setattr(st, "file_uploader", lambda *a, **k:
                        source if k.get("key") == "audit_upload" else real_uploader(*a, **k))
    at = app("audit_report")
    clean(at)
    clean(at.run())
    assert not offline["save_audit_report"].called
    at.button(key="audit_save_upload").click().run()
    offline["save_audit_report"].assert_called_once()
    clean(at.run())
    offline["save_audit_report"].assert_called_once()


@pytest.mark.parametrize("kind", ["esg", "early_warning", "ai"])
def test_identical_upload_and_manual_result_widgets(kind):
    snippets = {
        "esg": "from pages_modules.esg_scoring import _esegui_analisi_esg as show\n"
               "show({}, {}, {}, key_prefix='upload')\nshow({}, {}, {}, key_prefix='manual')",
        "early_warning": "from pages_modules.early_warning import _esegui_analisi_early_warning as show\n"
                         "show({}, key_prefix='upload')\nshow({}, key_prefix='manual')",
        "ai": "from pages_modules.ai_analyst import _mostra_relazione, genera_relazione_gestione\n"
              "r = genera_relazione_gestione({})\n_mostra_relazione(r, key_prefix='upload')\n"
              "_mostra_relazione(r, key_prefix='manual')",
    }
    clean(AppTest.from_string(snippets[kind], default_timeout=20).run())


def test_banking_latest_balance_is_not_first_statement_row():
    import pandas as pd
    from pages_modules.open_banking import analisi_flussi
    frame = pd.DataFrame({"data": ["2026-01-01", "2026-01-02"],
                          "importo": [100.0, -30.0], "saldo": [100.0, 70.0]})
    assert analisi_flussi(frame)["saldo_attuale"] == 70.0
    assert analisi_flussi(frame.iloc[::-1])["saldo_attuale"] == 70.0


def test_crisis_pdf_does_not_replace_zero_cashflow_with_profit_estimate():
    from utils.pdf_crisi_impresa import calcola_indici_ccii
    result = calcola_indici_ccii({"ebitda": 100_000, "operating_cashflow": 0,
                                 "debt_service": 20_000})
    assert result["dscr"]["valore"] == 0
    assert result["dscr"]["stato"] == "danger"
    result = calcola_indici_ccii({"ebitda": 0, "total_debt": 100_000})
    assert result["pfn_ebitda"]["stato"] == "danger"
