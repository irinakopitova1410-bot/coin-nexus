"""Regressions for informational crisis-indicator calculations and PDF output."""
import subprocess

import pytest

from utils.pdf_crisi_impresa import calcola_indici_ccii, generate_crisi_impresa_report


@pytest.mark.parametrize("extra", [
    {}, {"operating_cashflow": 80}, {"debt_service": 20},
    {"operating_cashflow": 80, "debt_service": 0},
    {"operating_cashflow": 80, "debt_service": -1},
    {"operating_cashflow": float("nan"), "debt_service": 20},
    {"operating_cashflow": 80, "debt_service": float("inf")},
])
def test_dscr_requires_actual_finite_cash_and_positive_service(extra):
    result = calcola_indici_ccii({"ebitda": 100, "total_debt": 1000, "interest_expense": 10, **extra})
    assert result["dscr"]["valore"] is None
    assert result["dscr"]["stato"] == "unavailable"
    assert result["_meta"]["unavailable_count"] > 0


@pytest.mark.parametrize("cash,expected,status", [(80, 4, "ok"), (0, 0, "danger"), (-20, -1, "danger")])
def test_dscr_uses_actual_cash_not_ebitda_estimate(cash, expected, status):
    result = calcola_indici_ccii({"ebitda": 500, "operating_cashflow": cash, "debt_service": 20})
    assert result["dscr"]["valore"] == expected
    assert result["dscr"]["stato"] == status


def test_zero_ebitda_is_not_replaced_by_ebit():
    result = calcola_indici_ccii({"ebitda": 0, "ebit": 100, "depreciation": 20, "interest_expense": 10, "total_debt": 100})
    assert result["interest_coverage"]["valore"] == 0
    assert result["pfn_ebitda"]["valore"] is None
    assert result["pfn_ebitda"]["stato"] == "danger"


def test_missing_ebitda_can_be_derived_from_reported_components():
    result = calcola_indici_ccii({"ebit": 100, "depreciation": 20, "interest_expense": 10})
    assert result["interest_coverage"]["valore"] == 12


def test_missing_cash_return_not_invented_and_empty_input_not_healthy():
    result = calcola_indici_ccii({"total_assets": 100, "ebitda": 100})
    assert result["ritorno_liquido_attivo"]["valore"] is None
    assert result["_meta"]["giudizio_stato"] != "ok"
    empty = calcola_indici_ccii({})
    assert empty["_meta"]["ok_count"] == 0
    assert empty["_meta"]["unavailable_count"] == 7


@pytest.mark.parametrize("data", [{}, {"equity": -100}, {"operating_cashflow": 80, "debt_service": 20}])
def test_pdf_renders_unavailable_and_actual_ratios_without_legal_diagnoses(tmp_path, data):
    output = generate_crisi_impresa_report("Audit Company", data, revisore="Reviewer")
    assert output.startswith(b"%PDF-")
    path = tmp_path / "report.pdf"
    path.write_bytes(output)
    text = subprocess.check_output(["pdftotext", str(path), "-"], text=True)
    assert "Soglia interna" in text
    assert "professionisti" in text
    assert "N/D" in text
    if "debt_service" in data:
        assert "Valore: 4.0" in text
    for forbidden in ("CRISI CONCLAMATA", "Obbligo di attivare", "Soglia normativa", "conforme", "entro 30 giorni"):
        assert forbidden not in text
