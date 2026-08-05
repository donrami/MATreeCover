"""Feature 009: endpoint threshold parameterization (T001).

The endpoint module imports torch lazily inside functions, so these
tests run locally without a GPU (OR-003).
"""

from __future__ import annotations

import pytest

from src.endpoint.server import THRESHOLD, _parse_threshold


def test_default_threshold_when_absent() -> None:
    assert _parse_threshold(None) == THRESHOLD
    assert _parse_threshold(THRESHOLD) == THRESHOLD


def test_numeric_threshold_passthrough() -> None:
    assert _parse_threshold(0.6) == 0.6
    assert _parse_threshold(0.65) == 0.65
    assert _parse_threshold("0.6") == 0.6  # JSON may deliver strings


def test_rejects_non_numeric() -> None:
    with pytest.raises(ValueError, match="threshold must be a number"):
        _parse_threshold("low")
    with pytest.raises(ValueError, match="threshold must be a number"):
        _parse_threshold([0.6])
    with pytest.raises(ValueError):
        _parse_threshold({"x": 1})


def test_rejects_out_of_range() -> None:
    with pytest.raises(ValueError, match="in \\(0, 1\\)"):
        _parse_threshold(0.0)
    with pytest.raises(ValueError, match="in \\(0, 1\\)"):
        _parse_threshold(1.0)
    with pytest.raises(ValueError, match="in \\(0, 1\\)"):
        _parse_threshold(1.5)
