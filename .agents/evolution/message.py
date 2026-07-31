"""Commit messages derived from the applied operation.

Answers the single question: *"how is a change described?"* Messages are
picked from per-operation template pools, so the wording always matches the
kind of change, and the recent history is consulted to avoid consecutive
repeats (e.g. three ``docs`` commits in a row).
"""

from __future__ import annotations

import random

# operation -> (commit type, [templates]). Templates use {module}, {name},
# {detail} and {version} placeholders.
TEMPLATES: dict[str, tuple[str, list[str]]] = {
    "add_helper": ("feat", ["add {name} helper", "add small {name} utility", "introduce {name} helper"]),
    "add_constant": ("refactor", ["define {name} constant", "extract {name} constant", "introduce {name} constant"]),
    "add_validation": ("fix", ["validate {detail} input", "add input validation for {detail}", "guard {detail} against bad input"]),
    "add_docstring": ("docs", ["document {name}", "improve docstring of {name}", "expand {name} docstring"]),
    "add_type_hint": ("refactor", ["add type hints to {name}", "annotate {name} with types", "type-hint {name}"]),
    "add_logging": ("feat", ["add module logging", "add debug logging", "instrument {module} with logging"]),
    "add_test": ("test", ["add tests for {name}", "cover {name} with tests", "add unit tests for {name}"]),
    "add_test_case": ("test", ["add {name} test case", "extend tests with {name} case", "add a case for {name}"]),
    "update_readme": ("docs", ["update usage examples", "refresh readme", "document {detail}"]),
    "version_bump": ("chore", ["bump version to {version}"]),
    "reorder_imports": ("style", ["sort imports", "reorder imports"]),
    "remove_dead_code": ("chore", ["remove unused {name}", "drop dead code", "clean up unused {name}"]),
    "change_default": ("fix", ["tune {name} default", "adjust {name} default value", "tweak {name} default"]),
    "add_parameter": ("feat", ["support {name} option", "add {name} parameter", "allow {name} to be configured"]),
    "new_module": ("feat", ["add {name} module", "add {name} module with helpers"]),
    "new_test_module": ("test", ["add {name} test suite", "add tests for {name} module"]),
    "cleanup_whitespace": ("style", ["trim trailing whitespace", "clean up whitespace"]),
}


def make(rng: random.Random, op: str, module: str, name: str, detail: str, version: str | None, history: list[str]) -> str:
    """Build a conventional commit message for the given operation."""
    if op not in TEMPLATES:
        return f"chore: update {module}"
    ctype, templates = TEMPLATES[op]

    # Avoid the same message twice within the recent window.
    options = templates
    if history:
        filtered = [t for t in options if _render(t, module, name, detail, version) not in history]
        if filtered:
            options = filtered

    body = _render(rng.choice(options), module, name, detail, version)
    scope = f"({module})" if module else ""
    return f"{ctype}{scope}: {body}"


def type_of(op: str) -> str:
    """Return the conventional commit type for an operation."""
    return TEMPLATES.get(op, ("chore", [""]))[0]


def _render(template: str, module: str, name: str, detail: str, version: str | None) -> str:
    return (
        template.replace("{module}", module)
        .replace("{name}", name)
        .replace("{detail}", detail)
        .replace("{version}", version or "")
    )
