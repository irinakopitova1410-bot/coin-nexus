"""Shared, repeatable CSV/Excel reading for page-specific field mappings."""

from utils.financial_import import read_financial_data


def read_financial_upload(uploaded_file):
    """Read from the start on every rerun; preserve the caller's stream position."""
    return read_financial_data(uploaded_file)
