"""Tests for the cli module."""

from __future__ import annotations

import poolhall.cli as mod


def test_module_imports():
    assert mod.__name__ == "poolhall.cli"


def test_public_api_surface():
    for name in "build_parser", "main":
        assert callable(getattr(mod, name)), f"missing {name}"
