"""Tests for the export module."""

from __future__ import annotations
import poolhall.export as mod


def test_module_imports():
    assert mod.__name__ == "poolhall.export"


def test_public_api_surface():
    for name in "to_csv", "export_inventory":
        assert callable(getattr(mod, name)), f"missing {name}"
