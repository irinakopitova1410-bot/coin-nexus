"""Regression tests for the engine-only financial calculation audit."""
import pytest

from engine.calculations import (
    altman_z_original, altman_z_prime, altman_z_doubleprime,
    calculate_credit_score, calculate_audit,
)
from engine.cashflow import calculate_cashflow
from engine.cost_optimizer import analyze_costs, simulate_cost_reduction
from engine.credit_readiness import BalanceInput, CreditReadinessEngine, analyze_credit_readiness
from engine.financial_ratios import calculate_all_ratios, _safe_div, _status
from engine.scoring import calculate_metrics


ALTMAN_MODELS = [
    (altman_z_original, [20, 100, 10, 15, 50, 40, 120], 2.825),
    (altman_z_prime, [20, 100, 10, 15, 50, 40, 120], 2.41675),
    (altman_z_doubleprime, [20, 100, 10, 15, 50, 40], 3.9585),
]


@pytest.mark.parametrize("model,args,expected", ALTMAN_MODELS)
def test_altman_published_coefficients(model, args, expected):
    assert model(*args).z_score == pytest.approx(round(expected, 3))


@pytest.mark.parametrize("model,args,expected", ALTMAN_MODELS)
@pytest.mark.parametrize("index,value", [(1, 0), (1, -1), (5, 0), (5, -1), (0, float("nan")), (3, float("inf"))])
def test_altman_rejects_invalid_inputs(model, args, expected, index, value):
    inputs = args.copy()
    inputs[index] = value
    with pytest.raises(ValueError):
        model(*inputs)


def test_negative_z_stress_is_not_an_improvement():
    result = altman_z_original(-100, 100, -100, -100, 0, 100, 0)
    for projection in result.projections:
        assert projection["Scenario Stress"] < result.z_score < projection["Scenario Base"]


@pytest.mark.parametrize("score,rating", [(84.9, "AA"), (69.5, "A"), (59.9, "BBB"), (49.5, "BB"), (39.9, "B"), (29.5, "CCC"), (14.9, "D"), (85, "AAA")])
def test_fractional_scores_do_not_fall_into_rating_gaps(score, rating):
    assert CreditReadinessEngine(BalanceInput())._score_to_rating(score)[0] == rating


def test_refinancing_does_not_raise_ebitda_or_multiply_credit_score():
    baseline = analyze_credit_readiness(fatturato=1000, ebitda=150)
    result = analyze_credit_readiness(fatturato=1000, ebitda=150, oneri_finanziari=100)
    assert len(result.azioni) == 1
    assert result.azioni[0].impatto_ebitda_eur == 0
    assert result.ebitda_potenziale == 150
    assert result.credito_potenziale_eur == baseline.credito_oggi_eur
    assert result.credit_score == baseline.credit_score


def test_readiness_rescores_actual_ebitda_improvement():
    result = analyze_credit_readiness(fatturato=1000, ebitda=150, costo_personale=290)
    # A small cost saving leaves EBITDA in the same score band: no invented +4.
    assert result.ebitda_potenziale == pytest.approx(155)
    expected = analyze_credit_readiness(fatturato=1000, ebitda=155)
    assert result.credito_potenziale_eur == pytest.approx(expected.credito_oggi_eur)


def ratios(data):
    result = calculate_all_ratios(data)
    return {ratio.name: ratio for category in result.categories for ratio in category.ratios}


def test_negative_equity_and_losses_are_not_healthy_roe_or_leverage():
    result = ratios({"total_assets": 100, "total_liabilities": 150, "net_income": -10})
    for name in ("Debt/Equity", "Equity Multiplier", "ROE"):
        assert result[name].status == "danger"
    assert result["ROE"].value == pytest.approx(0.2)


def test_zero_debt_ebitda_is_good_not_missing():
    result = ratios({"total_debt": 0, "ebitda": 10})
    assert result["Debt/EBITDA"].value == 0
    assert result["Debt/EBITDA"].status == "ok"


@pytest.mark.parametrize("ocf,capex,expected", [(0, 10, -0.1), (10, 10, 0)])
def test_zero_cashflow_is_not_treated_as_missing(ocf, capex, expected):
    result = ratios({"total_assets": 100, "operating_cashflow": ocf, "capex": capex})
    assert result["FCF Yield"].value == pytest.approx(expected)


def test_efficiency_uses_costs_not_revenue_and_keeps_zero_balances():
    result = ratios({"revenue": 1000, "cogs": 500, "purchases": 400,
                     "accounts_receivable": 0, "accounts_payable": 80, "inventory": 100})
    assert result["DSO — Giorni Credito"].value == 0
    assert result["DPO — Giorni Debito"].value == 73
    assert result["DIO — Giorni Magazzino"].value == 73
    assert result["CCC — Cash Conversion Cycle"].value == 0


def test_missing_cost_denominator_does_not_substitute_revenue():
    result = ratios({"revenue": 1000, "accounts_payable": 80, "inventory": 100})
    assert "DPO — Giorni Debito" not in result
    assert "DIO — Giorni Magazzino" not in result
    assert "CCC — Cash Conversion Cycle" not in result


def test_ratio_cash_uses_actual_cash_and_ebitda_adds_depreciation():
    result = ratios({"current_assets": 100, "current_liabilities": 50, "cash": 5,
                     "ebit": 10, "depreciation": 5, "revenue": 100})
    assert result["Cash Ratio"].value == 0.1
    assert result["EBITDA Margin"].value == 0.15


def test_nonfinite_safe_div_and_status_are_not_healthy():
    assert _safe_div(float("inf"), 1) is None
    assert _status(float("inf"), good_min=1) == "warning"


def test_cashflow_does_not_invent_historical_changes_debt_service_or_dividends():
    result = calculate_cashflow({"net_income": 100, "depreciation": 10, "current_assets": 500,
                                "current_liabilities": 200, "total_debt": 300, "fixed_assets": 400})
    assert result.delta_working_capital == 0
    assert result.operating_cashflow == 110
    assert result.capex == 10
    assert result.debt_repaid == result.dividends == result.financing_cashflow == 0
    assert any("stimato" in alert for alert in result.alerts)


def test_cashflow_indirect_method_and_repayment_alias_reconcile():
    result = calculate_cashflow({"net_income": 100, "depreciation": 20, "other_operating": 5,
        "current_assets": 300, "prev_current_assets": 250,
        "current_liabilities": 150, "prev_current_liabilities": 130,
        "capex": 40, "acquisitions": 10, "debt_issued": 20, "debt_repayment": 15, "dividends": 5})
    assert result.operating_cashflow == 95
    assert result.free_cashflow == 55
    assert result.investing_cashflow == -50
    assert result.financing_cashflow == 0
    assert result.net_change == 45


def test_cashflow_covenants_do_not_hide_losses_or_negative_capital():
    result = calculate_cashflow({"total_debt": 100, "ebitda": -10, "ebit": -20,
                                "interest_expense": 10, "equity": -200, "net_income": -100})
    assert len(result.covenants) == 3
    assert all("VIOLATO" in covenant["Status"] for covenant in result.covenants)
    for projection in result.projections:
        assert projection["OCF Stress"] < result.operating_cashflow < projection["OCF Base"]


@pytest.mark.parametrize("cash,expected,label", [(None, 5, "Debt / EBITDA (lordo)"), (60, 2, "Net Debt / EBITDA")])
def test_cashflow_net_debt_is_net_only_when_cash_is_known(cash, expected, label):
    data = {"total_debt": 100, "ebitda": 20}
    if cash is not None:
        data["cash"] = cash
    covenant = calculate_cashflow(data).covenants[0]
    assert covenant["Covenant"] == label
    assert covenant["Valore"] == expected


def test_nonoperating_costs_do_not_reduce_or_improve_ebitda():
    result = analyze_costs(1000, {"cogs": 600, "finance": 100, "depreciation": 100})
    assert result.current_ebitda_pct == 0.4
    assert result.ebitda_after_fix == 0.4
    assert all(item.impact_on_ebitda == 0 for item in result.items if item.key in {"finance", "depreciation"})
    simulation = simulate_cost_reduction(result, {"finance": 0.5, "depreciation": 0.5})
    assert simulation["total_savings_eur"] == 100
    assert simulation["new_ebitda_eur"] == 400
    assert sum(row["value"] for row in result.waterfall[1:-1]) + result.revenue == 400


def test_optimizer_does_not_lower_already_high_margin_with_arbitrary_cap():
    result = analyze_costs(1000, {"cogs": 200})
    assert result.ebitda_after_fix == result.current_ebitda_pct == 0.8


@pytest.mark.parametrize("reduction", [-0.1, 1.1, float("nan"), float("inf")])
def test_simulation_rejects_impossible_reductions(reduction):
    result = analyze_costs(1000, {"labor": 500})
    with pytest.raises(ValueError):
        simulate_cost_reduction(result, {"labor": reduction})


def test_negative_ebitda_does_not_generate_negative_loan_capacity():
    result = analyze_costs(1000, {"labor": 1500})
    simulation = simulate_cost_reduction(result, {})
    assert simulation["loan_capacity_before"] == simulation["loan_capacity_after"] == 0


def test_missing_debt_service_does_not_award_loss_making_empty_company_full_points():
    result = calculate_credit_score(-10, 0, 0, 0, 0, -10, 100, 0, 0, 0)
    assert result.components["DSCR (30%)"] == 0
    assert result.components["Current Ratio (20%)"] == 0


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
@pytest.mark.parametrize("entry", [
    lambda bad: calculate_cashflow({"net_income": bad}),
    lambda bad: calculate_all_ratios({"revenue": bad}),
    lambda bad: calculate_metrics({"debt": bad}),
    lambda bad: analyze_credit_readiness(fatturato=1000, ebitda=bad),
    lambda bad: analyze_costs(1000, {"labor": bad}),
    lambda bad: calculate_credit_score(0, 0, 0, 0, bad, 0, 0, 0, 0, 0),
    lambda bad: calculate_audit(100, 1000, 1000, 100, 5, bad, "low"),
])
def test_all_engines_reject_nonfinite_inputs(entry, bad):
    with pytest.raises(ValueError):
        entry(bad)


@pytest.mark.parametrize("control,errors", [(-1, 0), (11, 0), (5, -1), (5, 101)])
def test_audit_rejects_scores_and_error_rates_outside_documented_scale(control, errors):
    with pytest.raises(ValueError):
        calculate_audit(100, 1000, 1000, 100, control, errors, "low")


def test_model_probabilities_and_audit_opinions_are_explicitly_qualified():
    result = altman_z_original(20, 100, 10, 15, 50, 40, 120)
    assert "non calibrate" in result.recommendation
    readiness = analyze_credit_readiness(fatturato=1000, ebitda=100)
    assert "non delibera bancaria" in readiness.messaggio_principale
    audit = calculate_audit(100, 1000, 1000, 100, 10, 0, "low")
    assert audit.judgment.startswith("SIMULAZIONE")
    assert any("non consentono" in recommendation for recommendation in audit.recommendations)
