import io
from streamlit.testing.v1 import AppTest
from pages_modules import credit_readiness as page


def upload(text):
    source = io.BytesIO(text.encode())
    source.name = "Test.csv"
    return source


def test_partial_generic_file_is_not_scored():
    parsed = page._parse_uploaded_file(upload("campo,valore\nfatturato,1000\n"))
    assert parsed["requires_completion"]
    assert "ebitda" in parsed["missing_inputs"]


def test_complete_template_has_no_unused_dscr_requirement():
    source = io.BytesIO(page._get_cr_template_csv())
    source.name = "template.csv"
    parsed = page._parse_uploaded_file(source)
    assert parsed["missing_inputs"] == []


def test_import_prefills_only_known_values_and_preserves_edits(monkeypatch):
    state = {}
    monkeypatch.setattr(page.st, "session_state", state)
    parsed = {"data": {"fatturato": 1000}, "provided_fields": ["fatturato"], "company_name": "Test"}
    page._apply_readiness_upload(parsed, b"file")
    assert state["cr_fatturato"] == 1000
    assert state["cr_pc"] is None
    assert state["cr_company_name"] == "Test"
    state["cr_pc"] = 50
    page._apply_readiness_upload(parsed, b"file")
    assert state["cr_pc"] == 50
    page._apply_readiness_upload(parsed, b"new file")
    assert state["cr_pc"] is None


def test_manual_readiness_does_not_use_demo_numbers(monkeypatch):
    monkeypatch.setattr(page.st, "file_uploader", lambda *a, **kw: None)
    monkeypatch.setattr(page, "analyze_credit_readiness", lambda **kw: (_ for _ in ()).throw(AssertionError("Must not score blanks")))
    app = AppTest.from_string("from pages_modules.credit_readiness import render_credit_readiness\nrender_credit_readiness()").run()
    assert not app.exception
    assert all(widget.value is None for widget in app.number_input)
    app.button(key="cr_analizza_btn").click().run()
    assert not app.exception
    assert any("Inserisci almeno un dato" in item.value for item in app.warning)


def test_civil_upload_prefills_manual_form_without_scoring(monkeypatch):
    from test_civil_balance import upload as civil_upload
    source = civil_upload()
    monkeypatch.setattr(page.st, "file_uploader", lambda *a, **kw: source)
    monkeypatch.setattr(page, "analyze_credit_readiness", lambda **kw: (_ for _ in ()).throw(AssertionError("Must not score incomplete upload")))
    app = AppTest.from_string("from pages_modules.credit_readiness import render_credit_readiness\nrender_credit_readiness()").run()
    assert not app.exception
    assert app.number_input(key="cr_fatturato").value == 800
    assert app.number_input(key="cr_pc").value is None
    assert app.number_input(key="cr_cfo").value is None
    app.number_input(key="cr_pc").set_value(350).run()
    assert not app.exception
    assert app.number_input(key="cr_pc").value == 350


def test_history_retains_full_inputs_and_saves_changed_balance(monkeypatch):
    from types import SimpleNamespace
    from services import db
    state = {"user": {"id": "test-user", "access_token": "test-token"}}
    monkeypatch.setattr(page.st, "session_state", state)
    rows = []
    monkeypatch.setattr(db, "save_credit_report", lambda row, **kw: rows.append(row) or True)
    result = SimpleNamespace(credit_score=62.5, rating="B", messaggio_principale="Indicativo", stato="borderline", credito_oggi_eur=1, credito_potenziale_eur=2)
    inputs = dict(page.DEFAULTS, fatturato=1000, ebitda=100, attivo_corrente=200, passivo_corrente=100)
    page._save_readiness_history(result, "Test", inputs)
    page._save_readiness_history(result, "Test", inputs)
    assert len(rows) == 1
    assert isinstance(rows[0]["credit_score"], int)
    assert rows[0]["raw_data"]["input_finanziari"] == inputs
    inputs["patrimonio_netto"] = -50
    page._save_readiness_history(result, "Test", inputs)
    assert len(rows) == 2
