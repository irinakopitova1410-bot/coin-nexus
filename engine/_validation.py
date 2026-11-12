"""Small input guards shared by the financial engines."""
import math
from numbers import Number


def require_finite(**values):
    for name, value in values.items():
        try:
            valid = math.isfinite(value)
        except (TypeError, ValueError, OverflowError):
            valid = False
        if not valid:
            raise ValueError(f"{name} must be a finite number")


def validate_numeric_mapping(data):
    # Financial dictionaries may also carry company names and other metadata.
    require_finite(**{k: v for k, v in data.items() if isinstance(v, Number)})


def require_nonnegative(**values):
    require_finite(**values)
    for name, value in values.items():
        if value < 0:
            raise ValueError(f"{name} must be non-negative")
