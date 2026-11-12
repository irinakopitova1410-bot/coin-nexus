"""Regression tests for the real upload → diagnosis → completion workflow.

All fixture values are synthetic; no customer statements or credentials.
"""
import io
import math
import pytest
from streamlit.testing.v1 import AppTest
from engine.balance_diagnostics import analyze_available_balance, diagnostic_text
from pages_modules import credit_readiness as page


def upload(text):
    source = io.BytesIO(text.encode())
    source.name = "Example.csv"
    return source


def partial_upload():
    return upload("campo,valore\nazienda,Example\nfatturato,1000\nebit,-100\npatrimonio_netto,-50\n"
                  "totale_attivo,500\nebitda,-80\nfatturato_prev,1200\nattivo_corrente,150\n")


def render_app():
    return AppTest.from_string("from pages_modules.credit_readiness import render_credit_readiness\nrender_credit_readiness()").run(timeout=30)


def ratio(report, code):
    return next(row for row in report["ratios"] if row["code"] == code)


def forbidden(*args, **kwargs):
    pytest.fail("Must not invent a score or save records automatically")


def test_available_indicators_are_calculated_without_a_credit_score():
    report = analyze_available_balance({"fatturato": 1000, "ebit": -100, "ebitda": -80,
                                        "patrimonio_netto": -50, "totale_attivo": 500, "fatturato_prev": 1200})
    assert ratio(report, "ebit_margin")["value"] == -10
    assert ratio(report, "equity_ratio")["value"] == -10
    assert ratio(report, "revenue_growth")["value"] == pytest.approx(-100 / 6)
    for code in ("current_ratio", "debt_ebitda", "dscr"):
        assert ratio(report, code)["value"] is None
    assert report["credit_score"] is None
    assert report["estimated_credit"] is None
    assert report["signals"]


def test_missing_zero_and_negative_denominators_are_not_confused():
    report = analyze_available_balance({"fatturato": 1000, "ebit": 0, "ebitda": -20,
                                        "debiti_finanziari": 10, "attivo_corrente": 50, "passivo_corrente": 0})
    assert ratio(report, "ebit_margin")["value"] == 0
    assert ratio(report, "current_ratio")["value"] is None
    assert ratio(report, "debt_ebitda")["value"] is None
    assert ratio(report, "equity_ratio")["value"] is None


@pytest.mark.parametrize("invalid", [math.nan, math.inf, True, "wrong"])
def test_diagnostics_reject_invalid_values(invalid):
    with pytest.raises(ValueError):
        analyze_available_balance({"fatturato": invalid})


def test_download_contains_calculations_and_reported_ebitda_reconciliation():
    report = analyze_available_balance({"fatturato": 1000, "ebitda": -80},
                                       {"_source_period": "2025-01-31", "_reported_ebitda": -75})
    assert report["reconciliation"]["difference"] == 5
    text = diagnostic_text(report, "Example", ["Flusso di cassa operativo"]).decode()
    assert "-80,00 EUR" in text and "-75,00 EUR" in text
    assert "5,00 EUR" in text and "DSCR prospettico: N/D" in text
    assert "Flusso di cassa operativo" in text


@pytest.mark.parametrize("key", ["debiti_banche", "debiti_verso_banche", "debiti_totali", "total_debt"])
def test_partial_debt_captions_are_not_total_financing(key):
    parsed = page._parse_uploaded_file(upload(f"campo,valore\nfatturato,1000\n{key},500\n"))
    assert "debiti_finanziari" not in parsed["provided_fields"]


def test_partial_upload_shows_results_and_only_missing_completion_fields(monkeypatch):
    source = partial_upload()
    monkeypatch.setattr(page.st, "file_uploader", lambda *a, **kw: source)
    monkeypatch.setattr(page, "analyze_credit_readiness", forbidden)
    monkeypatch.setattr(page, "_save_readiness_history", forbidden)
    app = render_app()
    assert not app.exception
    assert any(metric.label == "Ricavi" and metric.value == "1.000 €" for metric in app.metric)
    assert any("Patrimonio netto negativo" in item.value for item in app.warning)
    assert app.button(key="cr_full_btn").disabled
    assert all(item.value is None for item in app.number_input if item.key.startswith("cr_extra_"))
    assert not any(item.key == "cr_extra_fatturato" for item in app.number_input)


def test_inline_completion_updates_ratio_and_prefills_manual_form(monkeypatch):
    source = partial_upload()
    monkeypatch.setattr(page.st, "file_uploader", lambda *a, **kw: source)
    monkeypatch.setattr(page, "analyze_credit_readiness", forbidden)
    monkeypatch.setattr(page, "_save_readiness_history", forbidden)
    app = render_app()
    app.number_input(key="cr_extra_passivo_corrente").set_value(100)
    next(button for button in app.button if button.label == "Aggiorna analisi con i dati integrati").click().run()
    assert not app.exception
    assert app.number_input(key="cr_pc").value == 100
    table = app.dataframe[0].value
    assert table.loc[table["Indicatore"] == "Liquidità corrente", "Valore"].iloc[0] == "1,50 x"
    app.run()
    assert not app.exception
    assert app.number_input(key="cr_extra_passivo_corrente").value == 100


def test_new_removed_and_invalid_files_do_not_leave_old_values(monkeypatch):
    current = [partial_upload()]
    monkeypatch.setattr(page.st, "file_uploader", lambda *a, **kw: current[0])
    app = render_app()
    app.number_input(key="cr_extra_passivo_corrente").set_value(100)
    next(button for button in app.button if button.label == "Aggiorna analisi con i dati integrati").click().run()
    current[0] = upload("campo,valore\nazienda,Second\nfatturato,2000\n")
    app.run()
    assert not app.exception
    assert app.number_input(key="cr_extra_passivo_corrente").value is None
    assert app.number_input(key="cr_fatturato").value == 2000
    current[0] = upload("invalid")
    app.run()
    assert not app.exception
    assert app.number_input(key="cr_fatturato").value is None
    assert not app.metric
    current[0] = partial_upload()
    app.run()
    current[0] = None
    app.run()
    assert not app.exception
    assert app.number_input(key="cr_fatturato").value is None
    assert not app.metric


def test_complete_file_requires_intent_and_is_not_automatically_saved(monkeypatch):
    source = io.BytesIO(page._get_cr_template_csv())
    source.name = "Example.csv"
    monkeypatch.setattr(page.st, "file_uploader", lambda *a, **kw: source)
    monkeypatch.setattr(page, "_save_readiness_history", forbidden)
    calls = []
    original = page.analyze_credit_readiness
    def compute(**kwargs):
        calls.append(kwargs)
        return original(**kwargs)
    monkeypatch.setattr(page, "analyze_credit_readiness", compute)
    app = render_app()
    assert not app.exception and not calls
    app.checkbox(key="cr_confirm_balance").check().run()
    app.button(key="cr_full_btn").click().run()
    assert not app.exception and len(calls) == 1
    app.run()
    assert not app.exception and len(calls) == 1
    app.button(key="cr_analizza_btn").click().run()
    assert not app.exception and len(calls) == 2
    assert len(app.get("plotly_chart")) == 6


def test_manual_partial_result_survives_reruns_and_invalidates_when_changed(monkeypatch):
    monkeypatch.setattr(page.st, "file_uploader", lambda *a, **kw: None)
    monkeypatch.setattr(page, "analyze_credit_readiness", forbidden)
    app = render_app()
    app.number_input(key="cr_fatturato").set_value(1000)
    app.number_input(key="cr_ebit").set_value(-100)
    app.button(key="cr_analizza_btn").click().run()
    assert not app.exception and app.metric
    app.run()
    assert not app.exception and app.metric
    app.number_input(key="cr_fatturato").set_value(2000).run()
    assert not app.exception and not app.metric


def test_duplicate_semantic_values_do_not_silently_override(monkeypatch):
    errors = []
    monkeypatch.setattr(page.st, "error", errors.append)
    assert page._parse_uploaded_file(upload("campo,valore\nfatturato,1000\nricavi,2000\n")) is None
    assert any("discordanti" in value for value in errors)
