"""Offline regression coverage for ERP templates and coherent fiscal rows."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.erp_connectors import (
    ERP_COLUMN_MAPS, OPTIONAL_FIELDS, REQUIRED_FIELDS,
    _detect_erp_type, get_template_df, parse_erp_file,
)


@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    import socket

    def blocked(*args, **kwargs):
        raise AssertionError("ERP audit must not access the network")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)


def parse(df):
    return parse_erp_file(df.to_csv(index=False).encode(), "erp.csv")


@pytest.mark.parametrize("erp_type", ["GENERIC", *ERP_COLUMN_MAPS])
def test_all_templates_round_trip_every_field(erp_type):
    frame = get_template_df(erp_type)
    # Distinct values ensure that mapping the right field is actually tested.
    frame.iloc[0] = range(101, 101 + len(frame.columns))
    result = parse(frame)
    assert result.success, result.error
    assert result.erp_type == erp_type
    assert result.missing_required == []
    assert result.rows_imported == 1
    if erp_type == "GENERIC":
        mapping = {col: col.lower().replace(" ", "_") for col in frame.columns}
    else:
        mapping = ERP_COLUMN_MAPS[erp_type]
    for col, target in mapping.items():
        if target in REQUIRED_FIELDS or target in OPTIONAL_FIELDS:
            assert result.data[target] == frame.iloc[0][col]


@pytest.mark.parametrize("columns", [
    ["EBIT", "EBITDA"],
    ["Revenue", "Equity", "Inventory", "Depreciation", "EBIT", "EBITDA"],
    ["TotalAssets", "CurrentAssets", "FiscalYear", "EBITDA"],
])
def test_common_labels_do_not_identify_a_vendor(columns):
    assert _detect_erp_type(columns) == "GENERIC"


@pytest.mark.parametrize("erp_type", ["GENERIC", *ERP_COLUMN_MAPS])
def test_latest_year_uses_one_row_and_never_backfills(erp_type):
    frame = get_template_df(erp_type)
    mapping = (ERP_COLUMN_MAPS[erp_type] if erp_type in ERP_COLUMN_MAPS else
               {col: col.lower().replace(" ", "_") for col in frame.columns})
    columns = {target: col for col, target in mapping.items()}
    # Newest fiscal year deliberately first, not last in file order.
    frame = pd.concat([frame] * 3, ignore_index=True)
    frame.loc[:, :] = 100.0
    frame[columns["year"]] = [2025, 2023, 2024]
    frame[columns["revenue"]] = [250, 230, 240]
    frame[columns["net_income"]] = [None, 23, 24]
    frame[columns["ebit"]] = [0, 3, 4]
    result = parse(frame)
    assert result.success, result.error
    assert result.data["year"] == 2025
    assert result.data["revenue"] == 250
    assert result.data["ebit"] == 0
    assert "net_income" not in result.data
    assert REQUIRED_FIELDS["net_income"] in result.missing_required


def test_standard_columns_survive_a_vendor_detection():
    result = parse(pd.DataFrame({
        "UMSATZ": [123], "total_assets": [900], "net_income": [12],
        "EBIT": [20], "EBITDA": [25],
    }))
    assert result.erp_type == "SAP"
    assert result.data["revenue"] == 123
    assert result.data["total_assets"] == 900
    assert result.data["net_income"] == 12


def test_without_fiscal_year_last_row_is_used_without_backfill():
    result = parse(pd.DataFrame({"revenue": [100, 200], "net_income": [10, None]}))
    assert result.data["revenue"] == 200
    assert "net_income" not in result.data


def test_equal_latest_year_uses_last_row():
    result = parse(pd.DataFrame({"year": [2025, 2024, 2025], "revenue": [1, 2, 3]}))
    assert result.data["revenue"] == 3
