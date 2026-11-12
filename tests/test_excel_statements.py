import io
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest
from utils.financial_import import read_financial_data


def workbook(sheets):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, rows in sheets.items():
            pd.DataFrame(rows).to_excel(writer, sheet_name=name, index=False, header=False)
    output.seek(0)
    output.name = "Example_Bilancio.xlsx"
    return output


def statements():
    return {
        "Stato Patrimoniale": [
            ["Example — Stato Patrimoniale", "", ""],
            ["VOCE DI BILANCIO", "31/01/2024 (EUR)", "31/01/2025 (EUR)"],
            ["TOTALE ATTIVO", 1100, 1000],
            ["TOTALE PATRIMONIO NETTO", 100, -100],
            ["TOTALE PASSIVO", 1100, 1000],
        ],
        "Conto Economico": [
            ["Example — Conto Economico", "", ""],
            ["VOCE", "31/01/2024 (EUR)", "31/01/2025 (EUR)"],
            ["A.1 Ricavi delle vendite e prestazioni", 900, 800],
            ["EBIT = A - B (Risultato Operativo)", -60, -40],
            ["Amm. immobilizzazioni immateriali", 10, 5],
            ["Amm. immobilizzazioni materiali", 20, 15],
        ],
        "Z-Score e Rischio": [["campo", "valore"], ["ebitda", 999999]],
    }


def test_multi_sheet_statements_titles_and_comparative_years():
    source = workbook(statements())
    data = read_financial_data(source)
    assert source.tell() == 0
    assert data["totale_attivo"] == 1000
    assert data["ricavi_netti"] == 800
    assert data["fatturato_prev"] == 900
    assert data["patrimonio_netto"] == -100
    assert data["ebitda"] == -20
    assert data["_source_period"] == "2025-01-31"
    assert data["_source_rows"]["ebit"]["sheet"] == "Conto Economico"
    assert "passivo_corrente" not in data
    assert "cash_flow_operativo" not in data


def test_periods_must_match_between_statements():
    sheets = statements()
    sheets["Conto Economico"][1][2] = "31/01/2026 (EUR)"
    with pytest.raises(ValueError, match="non coincidono"):
        read_financial_data(workbook(sheets))


def test_missing_statement_is_explicit_error():
    sheets = statements()
    sheets.pop("Conto Economico")
    with pytest.raises(ValueError, match="entrambi"):
        read_financial_data(workbook(sheets))


def test_generic_data_sheet_can_follow_cover():
    data = read_financial_data(workbook({
        "Copertina": [["Documento di bilancio"]],
        "Dati": [["campo", "valore"], ["fatturato", 800]],
    }))
    assert data["fatturato"] == 800


def test_multiple_generic_data_sheets_are_not_silently_merged():
    with pytest.raises(ValueError, match="più fogli"):
        read_financial_data(workbook({
            "Dati 1": [["campo", "valore"], ["fatturato", 800]],
            "Dati 2": [["campo", "valore"], ["fatturato", 900]],
        }))


def test_ai_preview_is_not_followed_by_false_unrecognized_error(monkeypatch):
    from pages_modules import ai_analyst
    source = workbook(statements())
    monkeypatch.setattr(ai_analyst.st, "file_uploader", lambda *a, **kw: source)
    monkeypatch.setattr(ai_analyst, "genera_relazione_gestione", lambda *a: pytest.fail("Incomplete data must not be scored"))
    app = AppTest.from_string("from pages_modules.ai_analyst import _tab_upload_ai\n_tab_upload_ai()").run()
    assert not app.exception
    assert not app.error
    assert len(app.dataframe) == 1
    assert app.info
