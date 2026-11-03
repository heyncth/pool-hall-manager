"""The change engine: small, valid, diverse edits.

Answers the single question: *"what gets changed?"* Every operation is
boundary-safe — it appends module-level blocks, rewrites a single known
signature line via ``ast.unparse`` (read-only parsing, never a rewrite of the
body), or edits files the project fully owns. Operations never mark generated
content with "AUTO" comments: the engine knows structure because it reads it.

Each op returns a :class:`Change` (or ``None`` when not applicable), and
``main.py`` runs the compile gate before anything is committed.
"""

from __future__ import annotations

import ast
import copy
import random
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import library  # noqa: E402

MODULE_DIRS = ("poolhall", "tests")
ROOT_FILES = ("README.md", "pyproject.toml")


@dataclass
class Change:
    """Description of one applied mutation."""

    op: str
    files: list[Path]
    module: str = ""          # commit scope; "" means no scope
    name: str = ""            # target function/constant/module
    detail: str = ""
    version: str | None = None


# ─── helpers ────────────────────────────────────────────────────────────────

def zone_py_files(repo: Path) -> list[Path]:
    """All tracked-area python files, relative to the repo root."""
    files: list[Path] = []
    for sub in MODULE_DIRS:
        base = repo / sub
        if base.exists():
            files.extend(sorted(p.relative_to(repo) for p in base.glob("*.py")))
    return files


def read_lines(repo: Path, rel: Path) -> list[str]:
    return (repo / rel).read_text(encoding="utf-8").splitlines()


def write_lines(repo: Path, rel: Path, lines: list[str]) -> None:
    (repo / rel).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def append_block(repo: Path, rel: Path, block: str) -> None:
    """Append a module-level block at the end of a file, safely spaced."""
    text = (repo / rel).read_text(encoding="utf-8").rstrip()
    (repo / rel).write_text(text + "\n\n" + block.rstrip() + "\n", encoding="utf-8")


def replace_line_range(repo: Path, rel: Path, start: int, end: int, new_lines: list[str]) -> None:
    """Replace 1-indexed lines ``start..end`` (inclusive)."""
    lines = read_lines(repo, rel)
    head = lines[: start - 1]
    tail = lines[end:]
    write_lines(repo, rel, head + new_lines + tail)


def module_of(rel: Path) -> str:
    """'poolhall/billing.py' -> 'billing'; 'tests/test_billing.py' -> 'billing'."""
    name = rel.stem
    return name[5:] if name.startswith("test_") else name


def test_file_for(module: str) -> Path:
    return Path("tests") / f"test_{module}.py"


def _is_production(rel: Path) -> bool:
    """True for files inside the poolhall package (not tests)."""
    return len(rel.parts) > 1 and rel.parts[0] == "poolhall"


def _is_test(rel: Path) -> bool:
    """True for files inside the tests directory."""
    return len(rel.parts) > 1 and rel.parts[0] == "tests"


def has_name(repo: Path, rel: Path, name: str) -> bool:
    text = (repo / rel).read_text(encoding="utf-8")
    return re.search(rf"\b{re.escape(name)}\b", text) is not None


def _source_of(repo: Path, rel: Path) -> str:
    return (repo / rel).read_text(encoding="utf-8")


def function_index(repo: Path, rel: Path) -> list[dict]:
    """Read-only index of top-level functions via ast."""
    source = _source_of(repo, rel)
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    funcs: list[dict] = []
    source_lines = source.splitlines()
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        header = source_lines[node.lineno - 1] if node.lineno <= len(source_lines) else ""
        funcs.append(
            {
                "name": node.name,
                "args": [a.arg for a in node.args.posonlyargs + node.args.args],
                "kwonly": [a.arg for a in node.args.kwonlyargs],
                "has_vararg": node.args.vararg is not None or node.args.kwarg is not None,
                "n_defaults": len(node.args.defaults),
                "lineno": node.lineno,
                "end_lineno": node.end_lineno,
                "single_line": header.lstrip().startswith("def ") and header.rstrip().endswith(":"),
                "has_decorators": bool(node.decorator_list),
                "docstring": ast.get_docstring(node),
            }
        )
    return funcs


def _simple_funcs(funcs: list[dict]) -> list[dict]:
    return [f for f in funcs if f["single_line"] and not f["has_vararg"] and not f["kwonly"]]


def _arg_type(name: str) -> str | None:
    """Guess a type hint for a parameter name, or None when unknown."""
    if any(k in name for k in ("count", "number", "minutes", "amount", "quantity", "total", "index", "step", "day")):
        return "int"
    if any(k in name for k in ("rate", "price", "percent", "cost", "factor")):
        return "float"
    if any(k in name for k in ("name", "label", "path", "text", "value", "note", "customer")):
        return "str"
    return None


def _node_for(typename: str) -> ast.expr:
    return ast.Name(id=typename, ctx=ast.Load())


def _signature_line(name: str, args_node: ast.arguments, returns: ast.expr | None) -> str:
    rendered = ast.unparse(args_node)
    line = f"def {name}({rendered})"
    if returns is not None:
        line += f" -> {ast.unparse(returns)}"
    return line + ":"


def _enhanced_docstring(func: dict) -> str | None:
    """Extend an existing docstring with real arg types, or None when nothing new can be said."""
    first_line = ""
    if func["docstring"]:
        first_line = func["docstring"].strip().splitlines()[0].rstrip(".")
    if not first_line:
        return None
    hints = {arg: _arg_type(arg) for arg in func["args"]}
    if not any(hints.values()):
        return None
    lines = [first_line + "."]
    if func["args"]:
        lines.append("")
        lines.append("Args:")
        for arg in func["args"]:
            lines.append(f"    {arg}: {hints[arg]}" if hints[arg] else f"    {arg}:")
    return "\n".join(lines)


# ─── file-level ops ─────────────────────────────────────────────────────────

def op_add_helper(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Append a new small helper function to a production module."""
    if not _is_production(rel):
        return None
    module = module_of(rel)
    pool = library.HELPERS.get(module, []) + library.helper_snippets()
    candidates = [(n, s) for n, s in pool if not has_name(repo, rel, n)]
    if not candidates:
        return None
    name, source = rng.choice(candidates)
    append_block(repo, rel, source)
    return Change(op="add_helper", files=[rel], module=module, name=name, detail=name)


def op_add_constant(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Append a new module-level constant to a production module."""
    if not _is_production(rel):
        return None
    module = module_of(rel)
    pool = library.CONSTANTS.get(module, []) + library.constant_snippets(module)
    candidates = [(n, v) for n, v in pool if not has_name(repo, rel, n)]
    if not candidates:
        return None
    name, value = rng.choice(candidates)
    append_block(repo, rel, f"{name} = {value}\n")
    return Change(op="add_constant", files=[rel], module=module, name=name, detail=name)


def op_add_validation(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Append an input validation helper to a production module."""
    if not _is_production(rel):
        return None
    module = module_of(rel)
    pool = library.VALIDATORS.get(module, []) + library.validator_snippets()
    candidates = [(n, s) for n, s in pool if not has_name(repo, rel, n)]
    if not candidates:
        return None
    name, source = rng.choice(candidates)
    append_block(repo, rel, source)
    return Change(op="add_validation", files=[rel], module=module, name=name, detail=name)


def op_add_docstring(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Expand the docstring of a production function that already has one."""
    if not _is_production(rel):
        return None
    funcs = [f for f in function_index(repo, rel) if f["docstring"] and not f["name"].startswith("_")]
    if not funcs:
        return None
    func = rng.choice(funcs)
    source = _source_of(repo, rel)
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == func["name"])
    doc_node = node.body[0]
    if not (isinstance(doc_node, ast.Expr) and isinstance(doc_node.value, ast.Constant) and isinstance(doc_node.value.value, str)):
        return None
    new_doc = _enhanced_docstring(func)
    if new_doc is None:
        return None
    indent = "    "
    doc_lines = [indent + '"""', *[indent + line for line in new_doc.splitlines()], indent + '"""']
    replace_line_range(repo, rel, doc_node.lineno, doc_node.end_lineno, doc_lines)
    return Change(op="add_docstring", files=[rel], module=module_of(rel), name=func["name"], detail=func["name"])


def op_add_type_hint(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Add type hints to a production function whose signature lacks some."""
    if not _is_production(rel):
        return None
    funcs = _simple_funcs(function_index(repo, rel))
    source = _source_of(repo, rel)
    tree = ast.parse(source)
    candidates: list[tuple[dict, ast.FunctionDef, ast.arguments, list[str | None]]] = []
    for func in funcs:
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == func["name"])
        args = copy.deepcopy(node.args)
        arg_names = [a.arg for a in args.posonlyargs + args.args]
        types = [_arg_type(name) for name in arg_names]
        annotatable = [a for a, t in zip(args.posonlyargs + args.args, types) if a.annotation is None and t is not None]
        if not annotatable and node.returns is not None:
            continue
        candidates.append((func, node, args, types))
    if not candidates:
        return None
    func, node, args, types = rng.choice(candidates)
    for index, a in enumerate(args.posonlyargs + args.args):
        hint = types[index]
        if a.annotation is None and hint is not None:
            a.annotation = _node_for(hint)
    returns = node.returns if node.returns is not None else _node_for("object")
    replace_line_range(repo, rel, func["lineno"], func["lineno"], [_signature_line(func["name"], args, returns)])
    return Change(op="add_type_hint", files=[rel], module=module_of(rel), name=func["name"], detail=func["name"])


def op_change_default(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Tweak a numeric default value of a production function parameter."""
    if not _is_production(rel):
        return None
    simple_names = {f["name"] for f in _simple_funcs(function_index(repo, rel))}
    source = _source_of(repo, rel)
    tree = ast.parse(source)
    candidates: list[tuple[ast.FunctionDef, ast.Constant, int]] = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or node.name not in simple_names:
            continue
        for index, default in enumerate(node.args.defaults):
            if isinstance(default, ast.Constant) and isinstance(default.value, (int, float)) and not isinstance(default.value, bool):
                candidates.append((node, default, index))
    if not candidates:
        return None
    node, default_node, default_index = rng.choice(candidates)
    args = copy.deepcopy(node.args)
    old_value = default_node.value
    new_value = rng.choice([1, 2, 5]) if old_value == 0 else old_value * rng.choice([2, 2, 3])
    args.defaults[default_index].value = new_value
    func = next(f for f in function_index(repo, rel) if f["name"] == node.name)
    replace_line_range(repo, rel, func["lineno"], func["lineno"], [_signature_line(node.name, args, node.returns)])
    return Change(op="change_default", files=[rel], module=module_of(rel), name=node.name, detail=node.name)


def op_add_parameter(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Append a new optional parameter (with default) to a simple production function."""
    if not _is_production(rel):
        return None
    funcs = [f for f in _simple_funcs(function_index(repo, rel)) if not f["name"].startswith("_")]
    if not funcs:
        return None
    func = rng.choice(funcs)
    source = _source_of(repo, rel)
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == func["name"])
    args = copy.deepcopy(node.args)
    param_name = rng.choice(["limit", "offset", "verbose", "strict", "dry_run", "force"])
    if any(a.arg == param_name for a in args.args):
        return None
    args.args.append(ast.arg(arg=param_name, annotation=None))
    args.defaults.append(ast.Constant(value=rng.choice([False, True, 0, 1, None])))
    replace_line_range(repo, rel, func["lineno"], func["lineno"], [_signature_line(func["name"], args, node.returns)])
    return Change(op="add_parameter", files=[rel], module=module_of(rel), name=param_name, detail=param_name)


def op_add_logging(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Add a module logger when the module does not have one yet."""
    if not _is_production(rel):
        return None
    text = _source_of(repo, rel)
    if "import logging" in text or "logging.getLogger" in text:
        return None
    lines = read_lines(repo, rel)
    import_idxs = [i for i, line in enumerate(lines) if line.startswith(("import ", "from "))]
    if import_idxs:
        insert_at = import_idxs[-1] + 1
    elif lines and lines[0].startswith('"""'):
        insert_at = 1
        if not lines[0].rstrip().endswith('"""'):
            while insert_at < len(lines) and not lines[insert_at].startswith('"""'):
                insert_at += 1
            insert_at += 1
    else:
        insert_at = 0
    lines.insert(insert_at, "import logging")
    if insert_at > 0 and lines[insert_at - 1].strip():
        lines.insert(insert_at, "")
    lines.append("")
    lines.append("logger = logging.getLogger(__name__)")
    write_lines(repo, rel, lines)
    return Change(op="add_logging", files=[rel], module=module_of(rel), name="logger", detail="module")


def op_reorder_imports(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Sort the top-level single-line import statements alphabetically."""
    source = _source_of(repo, rel)
    tree = ast.parse(source)
    imports = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    if len(imports) < 2:
        return None
    if any(n.lineno != n.end_lineno for n in imports):
        return None  # skip multi-line imports to avoid scrambling them
    lines = source.splitlines()
    start = imports[0].lineno
    end = imports[-1].end_lineno
    block = [line for line in lines[start - 1 : end] if line.strip()]
    future = [line for line in block if line.startswith("from __future__")]
    sorted_block = future + sorted(line for line in block if not line.startswith("from __future__"))
    if not sorted_block or block == sorted_block:
        return None
    replace_line_range(repo, rel, start, end, sorted_block)
    return Change(op="reorder_imports", files=[rel], module=module_of(rel), name="", detail="imports")


def op_tweak_literal(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Nudge a module-level numeric or bool constant to a nearby value."""
    if not _is_production(rel):
        return None
    try:
        tree = ast.parse(_source_of(repo, rel))
    except SyntaxError:
        return None
    candidates: list[tuple[str, int, int, int | float | bool]] = []
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        if not isinstance(node.targets[0], ast.Name):
            continue
        name = node.targets[0].id
        value = node.value
        if name.startswith("__"):
            continue
        if isinstance(value, ast.Constant) and isinstance(value.value, (int, float, bool)):
            candidates.append((name, node.lineno, node.end_lineno, value.value))
    if not candidates:
        return None
    name, lineno, end_lineno, old = rng.choice(candidates)
    lines = read_lines(repo, rel)
    if isinstance(old, bool):
        new: int | float | bool = not old
    elif isinstance(old, float):
        new = round(old + rng.choice([-1, -0.5, 0.5, 1]), 3)
    else:
        new = max(1, int(old) + rng.choice([-3, -2, -1, 1, 2, 3]))
    if new == old:
        return None
    line = lines[lineno - 1]
    updated, count = re.subn(
        rf"(\b{re.escape(name)}\s*=\s*){re.escape(repr(old))}\b",
        rf"\g<1>{repr(new)}",
        line,
        count=1,
    )
    if count == 0:
        return None  # value not a plain literal on that line; skip rather than mangle
    lines[lineno - 1] = updated
    write_lines(repo, rel, lines)
    return Change(op="tweak_literal", files=[rel], module=module_of(rel), name=name, detail=name)


def op_cleanup_whitespace(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Trim trailing whitespace and collapse excess blank lines."""
    lines = read_lines(repo, rel)
    result: list[str] = []
    blank_run = 0
    for line in lines:
        stripped = line.rstrip()
        if stripped == "":
            blank_run += 1
            if blank_run <= 2:
                result.append(stripped)
        else:
            blank_run = 0
            result.append(stripped)
    if result == lines:
        return None
    write_lines(repo, rel, result)
    return Change(op="cleanup_whitespace", files=[rel], module=module_of(rel), name="", detail="whitespace")


def op_remove_dead_code(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Delete a private helper or module constant that is referenced nowhere else."""
    candidates: list[tuple[str, int, int]] = []
    try:
        tree = ast.parse(_source_of(repo, rel))
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("_") and not node.decorator_list:
            candidates.append((node.name, node.lineno, node.end_lineno))
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if not name.startswith("__"):
                candidates.append((name, node.lineno, node.end_lineno))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            name = node.target.id
            if not name.startswith("__"):
                candidates.append((name, node.lineno, node.end_lineno))
    if not candidates:
        return None
    zone = zone_py_files(repo)
    for name, lineno, end_lineno in rng.sample(candidates, len(candidates)):
        referrers = [other for other in zone if other != rel and has_name(repo, other, name)]
        if any(_is_production(other) for other in referrers):
            continue  # alive in production code
        tests = [other for other in referrers if _is_test(other)]
        # only pair-delete when every covering test is a dedicated test_<name>
        # function; otherwise dropping the helper would break an unrelated test
        if any(not _has_dedicated_test(repo, t, name) for t in tests):
            continue
        lines = read_lines(repo, rel)
        whole = "\n".join(lines)
        if len(re.findall(rf"\b{re.escape(name)}\b", whole)) > 1:
            continue  # referenced elsewhere in the same file (or self-referential)
        del lines[lineno - 1 : end_lineno]
        if end_lineno < len(lines) and lines[end_lineno - 1] == "":
            del lines[end_lineno - 1]
        write_lines(repo, rel, lines)
        files = [rel]
        for test_rel in tests:
            if _drop_test_of(repo, test_rel, name):
                files.append(test_rel)
        return Change(op="remove_dead_code", files=files, module=module_of(rel), name=name, detail=name)
    return None


def _has_dedicated_test(repo: Path, test_rel: Path, helper: str) -> bool:
    """True when the test module has a test function for this helper only."""
    source = _source_of(repo, test_rel)
    return re.search(rf"\bdef test_{re.escape(helper)}\b", source) is not None


def _drop_test_of(repo: Path, test_rel: Path, helper: str) -> bool:
    """Delete test functions that only cover ``helper``; True when removed."""
    try:
        tree = ast.parse(_source_of(repo, test_rel))
    except SyntaxError:
        return False
    victims = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and (node.name == f"test_{helper}" or node.name.startswith(f"test_{helper}_"))
    ]
    if not victims:
        return False
    lines = read_lines(repo, test_rel)
    for node in sorted(victims, key=lambda n: n.lineno, reverse=True):
        del lines[node.lineno - 1 : node.end_lineno]
        if node.end_lineno < len(lines) and lines[node.end_lineno - 1] == "":
            del lines[node.end_lineno - 1]
    write_lines(repo, test_rel, lines)
    return True


# ─── tests / docs / meta ops ────────────────────────────────────────────────

def op_add_test(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Append a new test case to an existing test module."""
    if not _is_test(rel):
        return None
    module = module_of(rel)
    pool = library.TESTS_POOL.get(module)
    if not pool:
        return None
    candidates = [(n, s) for n, s in pool if not has_name(repo, rel, n)]
    if not candidates:
        return None
    name, source = rng.choice(candidates)
    append_block(repo, rel, source)
    return Change(op="add_test", files=[rel], module=module, name=name, detail=name)


def op_new_test_module(repo: Path, rng: random.Random) -> Change | None:
    """Create a test suite for a production module that has none yet."""
    modules: list[str] = []
    for py in zone_py_files(repo):
        if not _is_production(py):
            continue
        module = module_of(py)
        if not (repo / test_file_for(module)).exists():
            modules.append(module)
    if not modules:
        return None
    module = rng.choice(modules)
    funcs = [f for f in function_index(repo, Path("poolhall") / f"{module}.py") if not f["name"].startswith("_")]
    if not funcs:
        return None
    test_rel = test_file_for(module)
    content = _test_source(module, funcs)
    (repo / test_rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / test_rel).write_text(content, encoding="utf-8")
    return Change(op="new_test_module", files=[test_rel], module=module, name=module, detail=module)


def _test_source(module: str, funcs: list[dict]) -> str:
    """Build a test module: execute zero-arg public functions, assert the rest callable."""
    lines = [
        f'"""Tests for the {module} module."""',
        "",
        "from __future__ import annotations",
        "",
        f"import poolhall.{module} as mod",
    ]
    for func in funcs:
        lines.append("")
        if not func["args"] and not func["kwonly"] and not func["has_vararg"]:
            lines.append(f"def test_{func['name']}():")
            lines.append(f"    result = mod.{func['name']}()")
            lines.append("    assert result is not None")
        else:
            lines.append(f"def test_{func['name']}_exists():")
            lines.append(f"    assert callable(mod.{func['name']})")
    return "\n".join(lines) + "\n"


def op_new_module(repo: Path, rng: random.Random) -> Change | None:
    """Create a brand-new small module from the fixture pool."""
    available = [name for name in library.NEW_MODULES if not (repo / name).exists()]
    if not available:
        return None
    name = rng.choice(available)
    rel_path = Path(name)
    rel_path.parent.mkdir(parents=True, exist_ok=True)
    (repo / rel_path).write_text(library.NEW_MODULES[name], encoding="utf-8")
    return Change(op="new_module", files=[rel_path], module=rel_path.stem, name=rel_path.stem, detail=rel_path.stem)


def op_update_readme(repo: Path, rng: random.Random) -> Change | None:
    """Append a README section that is not already present."""
    rel = Path("README.md")
    if not (repo / rel).exists():
        return None
    text = _source_of(repo, rel)
    candidates = [section for section in library.README_SECTIONS if section[0] not in text]
    if not candidates:
        return None
    heading, body = rng.choice(candidates)
    append_block(repo, rel, heading + "\n\n" + body)
    return Change(op="update_readme", files=[rel], module="", name="", detail=heading.lstrip("#").strip().lower())


def op_version_bump(repo: Path, rng: random.Random) -> Change | None:
    """Bump the version in pyproject.toml."""
    rel = Path("pyproject.toml")
    if not (repo / rel).exists():
        return None
    text = _source_of(repo, rel)
    match = re.search(r'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', text)
    if not match:
        return None
    major, minor, patch = (int(g) for g in match.groups())
    if rng.random() < 0.3:
        new_version = f"{major}.{minor + 1}.0"
    else:
        new_version = f"{major}.{minor}.{patch + 1}"
    updated = text.replace(match.group(0), f'version = "{new_version}"')
    (repo / rel).write_text(updated, encoding="utf-8")
    return Change(op="version_bump", files=[rel], module="", name="", detail="", version=new_version)


# ─── registry ───────────────────────────────────────────────────────────────

FileOp = Callable[[Path, random.Random, Path], Change | None]
MetaOp = Callable[[Path, random.Random], Change | None]

FILE_OPS: dict[str, FileOp] = {
    "add_helper": op_add_helper,
    "add_constant": op_add_constant,
    "add_validation": op_add_validation,
    "add_docstring": op_add_docstring,
    "add_type_hint": op_add_type_hint,
    "change_default": op_change_default,
    "add_parameter": op_add_parameter,
    "add_logging": op_add_logging,
    "reorder_imports": op_reorder_imports,
    "cleanup_whitespace": op_cleanup_whitespace,
    "remove_dead_code": op_remove_dead_code,
    "tweak_literal": op_tweak_literal,
    "add_test": op_add_test,
}

META_OPS: dict[str, MetaOp] = {
    "new_module": op_new_module,
    "new_test_module": op_new_test_module,
    "update_readme": op_update_readme,
    "version_bump": op_version_bump,
}

FILE_WEIGHTS: dict[str, int] = {
    "add_helper": 6,
    "add_docstring": 10,
    "add_type_hint": 9,
    "add_test": 9,
    "add_constant": 6,
    "add_validation": 6,
    "reorder_imports": 5,
    "cleanup_whitespace": 5,
    "change_default": 5,
    "add_parameter": 5,
    "remove_dead_code": 10,
    "tweak_literal": 5,
}

META_WEIGHTS: dict[str, int] = {
    "new_module": 2,
    "new_test_module": 2,
    "update_readme": 3,
    "version_bump": 2,
}


def try_file_op(repo: Path, rng: random.Random, op: str, rel: Path) -> Change | None:
    """Attempt one file-level op; returns None when not applicable."""
    return FILE_OPS[op](repo, rng, rel)


def try_meta_op(repo: Path, rng: random.Random, op: str) -> Change | None:
    """Attempt one meta-level op."""
    return META_OPS[op](repo, rng)
