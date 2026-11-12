"""Regression checks for the CSV/Excel entry points and upload widget state."""

import io
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pages_modules._file_import import read_financial_upload
from pages_modules.credit_readiness import _parse_uploaded_file
from pages_modules.ai_analyst import parse_csv_ai
from pages_modules.early_warning import parse_csv_early_warning
from pages_modules.whatif_simulator import parse_csv_whatif
from pages_modules.audit_report import _parse_audit_file, _safe_float
from pages_modules.variance_analysis import parse_variance_csv, _apply_variance_upload


def upload(text, name="data.csv"):
    stream = io.BytesIO(text.encode("utf-8"))
    stream.name = name
    return stream


def test_shared_upload_displays_source_warnings(monkeypatch):
    import pages_modules._file_import as helper
    data = {"ebitda": 10, "_import_warnings": ["Missing cash flow", "Latest year selected"]}
    shown = []
    monkeypatch.setattr(helper, "read_financial_data", lambda source: data)
    monkeypatch.setattr("streamlit.warning", shown.append)
    assert helper.read_financial_upload(upload("")) is data
    assert shown == data["_import_warnings"]


@pytest.mark.parametrize("module,parser", [
    ("ai_analyst", "parse_csv_ai"),
    ("early_warning", "parse_csv_early_warning"),
    ("whatif_simulator", "parse_csv_whatif"),
])
def test_civil_data_does_not_trigger_ungrounded_risk_analysis(monkeypatch, module, parser):
    import importlib
    page = importlib.import_module("pages_modules." + module)
    data = {"fatturato": 1000, "_source_format": "civil_balance"}
    previews = []
    monkeypatch.setattr(page, "read_financial_upload", lambda source: data)
    monkeypatch.setattr(page, "show_import_preview", previews.append)
    assert getattr(page, parser)(upload("")) is None
    assert previews == [data]


@pytest.mark.parametrize("module,parser,renderer", [
    ("risk_analysis", "parse_zscore_file", "render_risk_analysis"),
    ("financial_ratios", "parse_ratios_file", "render_financial_ratios"),
    ("credit_scoring", "parse_credit_file", "show_credit_scoring"),
    ("cashflow_analysis", "parse_financial_file", "render_cashflow_analysis"),
])
def test_completion_wrappers_show_preview_and_keep_manual_form(monkeypatch, module, parser, renderer):
    import importlib
    import streamlit as st
    from streamlit.testing.v1 import AppTest
    page = importlib.import_module("pages_modules." + module)
    source = upload("")
    source.size = 0
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: source)
    monkeypatch.setattr(page, parser, lambda source: {
        "success": False, "requires_completion": True, "error": "Missing inputs",
        "extracted_data": {"fatturato": 1000, "_source_period": "31-01-2025",
                           "_import_warnings": ["SOURCE LIMITATION"]},
    })
    app = AppTest.from_string(
        f"from pages_modules.{module} import {renderer}\n{renderer}()"
    ).run(timeout=30)
    assert not app.exception
    assert any("SOURCE LIMITATION" in item.value for item in app.warning)
    assert any("completa i dati mancanti" in item.value for item in app.warning)
    assert len(app.dataframe) >= 1
    assert len(app.number_input) >= 1


def test_readiness_never_maps_total_liabilities_to_current(monkeypatch):
    import pages_modules.credit_readiness as page
    for key in ("totale_passivo", "totale_passivita", "total_liabilities"):
        assert key not in page.FIELD_MAP
    monkeypatch.setattr(page, "read_financial_upload", lambda source: {
        "fatturato": 1000, "totale_passivita": 500,
        "debiti_esigibili_entro_esercizio_successivo": 200,
        "_source_format": "civil_balance",
    })
    parsed = page._parse_uploaded_file(upload(""))
    assert "passivo_corrente" not in parsed["provided_fields"]
    assert set(parsed["missing_inputs"]) == {
        "passivo_corrente", "cash_operativo", "rimborso_debito (DSCR)"
    }


def test_incomplete_civil_readiness_only_shows_preview(monkeypatch):
    from streamlit.testing.v1 import AppTest
    import streamlit as st
    import pages_modules.credit_readiness as page

    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: upload(""))
    monkeypatch.setattr(page, "read_financial_upload", lambda source: {
        "fatturato": 1000, "ebitda": 100, "_source_format": "civil_balance"
    })
    def forbidden(*args, **kwargs):
        raise AssertionError("Incomplete civil data must not be scored or saved")
    monkeypatch.setattr(page, "analyze_credit_readiness", forbidden)
    monkeypatch.setattr(page, "_save_readiness_history", forbidden)
    app = AppTest.from_string(
        "from pages_modules.credit_readiness import render_credit_readiness\n"
        "render_credit_readiness()"
    ).run(timeout=30)
    assert not app.exception
    assert any("non calcolata né salvata" in item.value for item in app.warning)
    assert len(app.dataframe) >= 1


@pytest.mark.parametrize("parser,key", [
    (_parse_uploaded_file, "ebitda"),
    (parse_csv_ai, "ebitda"),
    (parse_csv_early_warning, "ebitda"),
    (parse_csv_whatif, "ebitda"),
])
@pytest.mark.parametrize("text", [
    "campo,valore\nazienda,Test SRL\nfatturato,1000.50\nebitda,123.45\n",
    'campo;valore\nazienda;Test SRL\nfatturato;1.000,50\nebitda;123,45\n',
    "azienda,fatturato,ebitda\nTest SRL,1000.50,123.45\n",
    "azienda,Test SRL\nfatturato,1000.50\nebitda,123.45\n",
])
def test_financial_page_formats_and_repeat_reads(parser, key, text):
    source = upload(text)
    for _ in range(2):
        result = parser(source)
        assert result is not None
        assert result.get("data", result)[key] == pytest.approx(123.45)
        assert source.tell() == 0


def test_credit_readiness_rejects_unknown_or_invalid_file(monkeypatch):
    monkeypatch.setattr("streamlit.error", lambda *args, **kwargs: None)
    assert _parse_uploaded_file(upload("campo,valore\nbanana,123\n")) is None
    assert _parse_uploaded_file(upload('campo;valore\nfatturato;not-money\n')) is None
    assert _parse_uploaded_file(upload("")) is None


def test_valid_zero_values_remain_zero():
    source = upload("campo,valore\nfatturato,1000\nebitda,0\nzscore,0\n")
    assert parse_csv_whatif(source)["ebitda"] == 0
    assert parse_csv_ai(source)["zscore"] == 0


def test_excel_uses_same_fields_and_number_conversion():
    source = io.BytesIO()
    source.name = "data.xlsx"
    pd.DataFrame([
        ["campo", "valore"], ["azienda", "Test SRL"],
        ["fatturato", 1000.50], ["ebitda", 123.45],
    ]).to_excel(source, index=False, header=False)
    source.seek(0)
    assert _parse_uploaded_file(source)["data"]["ebitda"] == pytest.approx(123.45)
    assert parse_csv_whatif(source)["ebitda"] == pytest.approx(123.45)
    assert source.tell() == 0


def test_audit_unified_template_alias_and_italian_amount():
    source = upload('campo;valore\nrisultato_ante_imposte;1.234,56\n')
    data = _parse_audit_file(source)
    assert _safe_float(data["pre_tax_income"]) == pytest.approx(1234.56)


def test_variance_first_row_decimal_and_repeat_reads():
    source = upload("ricavi_budget,1000.50\nricavi_actual,900.25\n")
    for _ in range(2):
        data = parse_variance_csv(source)
        assert data == {"ricavi_budget": 1000.5, "ricavi_actual": 900.25}
        assert source.tell() == 0


def test_variance_upload_replaces_existing_widgets_once(monkeypatch):
    state = {"vb_ricavi_b": 195000000.0, "var_pdf": b"outdated"}
    monkeypatch.setattr("streamlit.session_state", state)
    _apply_variance_upload({"ricavi_budget": 100.5}, "first")
    assert state["vb_ricavi_b"] == 100.5
    assert state["vb_cogs_b"] == 0
    assert "var_pdf" not in state
    state["vb_ricavi_b"] = 200.0
    _apply_variance_upload({"ricavi_budget": 100.5}, "first")
    assert state["vb_ricavi_b"] == 200.0
    _apply_variance_upload({"ricavi_budget": 300.0}, "second")
    assert state["vb_ricavi_b"] == 300.0


def test_variance_real_widgets_update_after_initial_render(monkeypatch):
    from streamlit.testing.v1 import AppTest
    import streamlit as st

    current = [None]
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: current[0])
    app = AppTest.from_string(
        "from pages_modules.variance_analysis import show_variance_analysis\n"
        "show_variance_analysis()"
    ).run(timeout=30)
    assert not app.exception
    current[0] = upload("ricavi_budget,1000.50\nricavi_actual,900.25\n")
    app.run(timeout=30)
    assert not app.exception
    assert app.number_input(key="vb_ricavi_b").value == 1000.5
    assert app.number_input(key="vb_cogs_b").value == 0
    app.number_input(key="vb_ricavi_b").set_value(1200.0).run(timeout=30)
    assert not app.exception
    assert app.number_input(key="vb_ricavi_b").value == 1200.0


def test_credit_readiness_upload_and_manual_results_have_unique_widgets(monkeypatch):
    from streamlit.testing.v1 import AppTest
    import streamlit as st
    from pages_modules.credit_readiness import _get_cr_template_csv

    source = io.BytesIO(_get_cr_template_csv())
    source.name = "template.csv"
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: source)
    app = AppTest.from_string(
        "from pages_modules.credit_readiness import render_credit_readiness\n"
        "render_credit_readiness()"
    ).run(timeout=30)
    assert not app.exception
    app.button(key="cr_analizza_btn").click().run(timeout=30)
    assert not app.exception


def test_whatif_manual_simulator_survives_slider_and_preset_reruns():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_string(
        "from pages_modules.whatif_simulator import show_whatif_simulator\n"
        "show_whatif_simulator()"
    ).run(timeout=30)
    assert not app.exception
    app.button[0].click().run(timeout=30)
    assert not app.exception
    assert app.slider(key="whatif_manual_result_delta_fatturato").value == 0
    app.slider(key="whatif_manual_result_delta_fatturato").set_value(10).run(timeout=30)
    assert not app.exception
    assert app.slider(key="whatif_manual_result_delta_fatturato").value == 10
    app.button(key="whatif_manual_result_preset_0").click().run(timeout=30)
    assert not app.exception
    assert app.slider(key="whatif_manual_result_delta_fatturato").value == -20
    app.slider(key="whatif_manual_result_delta_costi_pers").set_value(5).run(timeout=30)
    assert not app.exception
    assert app.slider(key="whatif_manual_result_delta_fatturato").value == -20


def test_banking_reads_excel_and_italian_amounts(monkeypatch):
    from streamlit.testing.v1 import AppTest
    import streamlit as st

    source = io.BytesIO()
    source.name = "bank.xlsx"
    pd.DataFrame({
        "data": ["2025-01-01", "2025-01-02"],
        "descrizione": ["Incasso", "Pagamento"],
        "importo": ["1.234,56", "-100,25"],
        "saldo": ["2.000,00", "1.899,75"],
    }).to_excel(source, index=False)
    source.seek(0)
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: source)
    app = AppTest.from_string(
        "from pages_modules.open_banking import _tab_upload_estratto\n"
        "_tab_upload_estratto()"
    ).run(timeout=30)
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "€1,235"
    assert app.metric[1].value == "€100"


def test_excel_native_precision_is_not_reinterpreted_as_ambiguous_text():
    source = io.BytesIO()
    source.name = "native.xlsx"
    pd.DataFrame([["campo", "valore"], ["ebitda", 1.234], ["tasso_errori", 1.234]]).to_excel(
        source, index=False, header=False)
    source.seek(0)
    assert parse_csv_whatif(source)["ebitda"] == pytest.approx(1.234)
    assert _parse_audit_file(source)["error_rate"] == pytest.approx(1.234)


@pytest.mark.parametrize("parser,field", [
    (_parse_uploaded_file, "ebitda"), (parse_csv_ai, "ebitda"),
    (parse_csv_early_warning, "ebitda"), (parse_csv_whatif, "ebitda"),
    (_parse_audit_file, "tasso_errori"),
])
def test_ambiguous_text_is_a_user_error_not_a_runtime_exception(monkeypatch, parser, field):
    errors = []
    monkeypatch.setattr("streamlit.error", lambda message, **kwargs: errors.append(message))
    assert parser(upload(f"campo,valore\n{field},1.234\n")) is None
    assert any("ambiguo" in message.lower() for message in errors)


def test_variance_pdf_invalidated_for_each_report_input(monkeypatch):
    from pages_modules.variance_analysis import _invalidate_variance_pdf
    state = {}
    monkeypatch.setattr("streamlit.session_state", state)
    inputs = ["Company", "2025", {"ricavi_budget": 10.0}, [("BU", 1.0, 2.0)], [("Driver", 3.0)]]
    _invalidate_variance_pdf(*inputs)
    state["var_pdf"] = b"report"
    _invalidate_variance_pdf(*inputs)
    assert "var_pdf" in state
    for index, replacement in enumerate([
        "Other", "2026", {"ricavi_budget": 20.0}, [("BU", 2.0, 2.0)], [("Driver", 4.0)]
    ]):
        changed = list(inputs)
        changed[index] = replacement
        state["var_pdf"] = b"report"
        _invalidate_variance_pdf(*changed)
        assert "var_pdf" not in state
        _invalidate_variance_pdf(*inputs)


@pytest.mark.parametrize("kind", ["risk", "ratios", "cashflow", "credit"])
def test_identical_upload_and_manual_result_renderers_have_unique_keys(monkeypatch, kind):
    from streamlit.testing.v1 import AppTest
    import services.db as db
    monkeypatch.setattr(db, "save_credit_report", lambda *args, **kwargs: True)
    monkeypatch.setattr(db, "save_risk_analysis", lambda *args, **kwargs: True)
    import pages_modules.risk_analysis as risk_page
    monkeypatch.setattr(risk_page, "save_risk_analysis", lambda *args, **kwargs: True)
    script = '''
from pages_modules.risk_analysis import _show_zscore_result
from pages_modules.financial_ratios import _show_ratio_result
from pages_modules.cashflow_analysis import _run_cashflow
from pages_modules.credit_scoring import _show_credit_result
from engine.calculations import altman_z_original, calculate_credit_score
from engine.financial_ratios import calculate_all_ratios
data = {"total_assets": 1000.0, "total_debt": 500.0, "total_equity": 500.0,
        "revenue": 1000.0, "ebit": 100.0, "ebitda": 120.0,
        "current_assets": 300.0, "current_liabilities": 200.0}
for suffix in ("auto", "manual"):
    if KIND == "risk":
        result = altman_z_original(1000, 100, 50, 100, 500, 500, 1000)
        _show_zscore_result(result, data, "Company", "Manifatturiero", key_suffix=suffix)
    elif KIND == "ratios":
        _show_ratio_result(calculate_all_ratios(data), "Company", "Manifatturiero", key_suffix=suffix)
    elif KIND == "cashflow":
        _run_cashflow(data, "Company", key_suffix=suffix)
    else:
        result = calculate_credit_score(100, 20, 10, 20, 500, 120, 1000, 300, 200, 500)
        _show_credit_result(result, "Company", key_suffix=suffix)
'''
    app = AppTest.from_string("KIND = " + repr(kind) + "\n" + script).run(timeout=30)
    assert not app.exception
