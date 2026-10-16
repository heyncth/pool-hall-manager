"""Tests for the notifications module."""

from __future__ import annotations
import poolhall.notifications as mod


def test_module_imports():
    assert mod.__name__ == "poolhall.notifications"


def test_public_api_surface():
    for name in "low_stock_notices", "reservation_notice":
        assert callable(getattr(mod, name)), f"missing {name}"
