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
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        args_text = ast.get_source_segment(source, node.args)
        funcs.append(
            {
                "name": node.name,
                "args": [a.arg for a in node.args.posonlyargs + node.args.args],
                "kwonly": [a.arg for a in node.args.kwonlyargs],
                "has_vararg": node.args.vararg is not None or node.args.kwarg is not None,
                "n_defaults": len(node.args.defaults),
                "lineno": node.lineno,
                "end_lineno": node.end_lineno,
                "single_line": args_text is not None and "\n" not in args_text,
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


def _enhanced_docstring(func: dict) -> str:
    """Build a fuller docstring from an existing one and the real signature."""
    first_line = ""
    if func["docstring"]:
        first_line = func["docstring"].strip().splitlines()[0].rstrip(".")
    if not first_line:
        first_line = f"Describe what {func['name']} does"
    lines = [first_line + ".", "", "Args:"]
    if func["args"]:
        lines.extend(f"    {arg}: Description." for arg in func["args"])
    else:
        lines.append("    (none)")
    lines.extend(["", "Returns:", "    Description."])
    return "\n".join(lines)


# ─── file-level ops ─────────────────────────────────────────────────────────

def op_add_helper(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Append a new small helper function to a production module."""
    if not _is_production(rel):
        return None
    module = module_of(rel)
    pool = library.HELPERS.get(module)
    if not pool:
        return None
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
    pool = library.CONSTANTS.get(module)
    if not pool:
        return None
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
    pool = library.VALIDATORS.get(module)
    if not pool:
        return None
    candidates = [(n, s) for n, s in pool if not has_name(repo, rel, n)]
    if not candidates:
        return None
    name, source = rng.choice(candidates)
    append_block(repo, rel, source)
    return Change(op="add_validation", files=[rel], module=module, name=name, detail=name)


def op_add_docstring(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Expand the docstring of a function that already has one."""
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
    indent = "    "
    doc_lines = [indent + '"""', *[indent + line for line in new_doc.splitlines()], indent + '"""']
    replace_line_range(repo, rel, doc_node.lineno, doc_node.end_lineno, doc_lines)
    return Change(op="add_docstring", files=[rel], module=module_of(rel), name=func["name"], detail=func["name"])


def op_add_type_hint(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Add type hints to a function whose signature lacks some."""
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
    """Tweak a numeric default value of a function parameter."""
    simple_names = {f["name"] for f in _simple_funcs(function_index(repo, rel))}
    source = _source_of(repo, rel)
    tree = ast.parse(source)
    candidates: list[tuple[ast.FunctionDef, ast.Constant]] = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or node.name not in simple_names:
            continue
        for default in node.args.defaults:
            if isinstance(default, ast.Constant) and isinstance(default.value, (int, float)) and not isinstance(default.value, bool):
                candidates.append((node, default))
    if not candidates:
        return None
    node, default_node = rng.choice(candidates)
    args = copy.deepcopy(node.args)
    old_value = default_node.value
    new_value = rng.choice([1, 2, 5]) if old_value == 0 else old_value * rng.choice([2, 2, 3])
    for default in args.defaults:
        if isinstance(default, ast.Constant) and default.value == old_value:
            default.value = new_value
    func = next(f for f in function_index(repo, rel) if f["name"] == node.name)
    replace_line_range(repo, rel, func["lineno"], func["lineno"], [_signature_line(node.name, args, node.returns)])
    return Change(op="change_default", files=[rel], module=module_of(rel), name=node.name, detail=node.name)


def op_add_parameter(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Append a new optional parameter (with default) to a simple function."""
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
    block = lines[start - 1 : end]
    sorted_block = sorted(line for line in block if line.strip())
    if not sorted_block or block == sorted_block:
        return None
    replace_line_range(repo, rel, start, end, sorted_block)
    return Change(op="reorder_imports", files=[rel], module=module_of(rel), name="", detail="imports")


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
    """Delete a private helper that is referenced nowhere else."""
    funcs = [f for f in function_index(repo, rel) if f["name"].startswith("_") and not f["has_decorators"]]
    if not funcs:
        return None
    zone = zone_py_files(repo)
    for func in rng.sample(funcs, len(funcs)):
        name = func["name"]
        if any(other != rel and has_name(repo, other, name) for other in zone):
            continue
        lines = read_lines(repo, rel)
        whole = "\n".join(lines)
        if len(re.findall(rf"\b{re.escape(name)}\b", whole)) > 1:
            continue  # referenced elsewhere in the same file (or self-recursive)
        del lines[func["lineno"] - 1 : func["end_lineno"]]
        if func["end_lineno"] < len(lines) and lines[func["end_lineno"] - 1] == "":
            del lines[func["end_lineno"] - 1]
        write_lines(repo, rel, lines)
        return Change(op="remove_dead_code", files=[rel], module=module_of(rel), name=name, detail=name)
    return None


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


def op_new_test_module(repo: Path, rng: random.Random, rel: Path) -> Change | None:
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
    funcs = [f["name"] for f in function_index(repo, Path("poolhall") / f"{module}.py") if not f["name"].startswith("_")]
    if not funcs:
        return None
    test_rel = test_file_for(module)
    names = ", ".join(f'"{n}"' for n in funcs[:6])
    content = library.NEW_TEST_TEMPLATE.format(module=module, names=names)
    (repo / test_rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / test_rel).write_text(content, encoding="utf-8")
    return Change(op="new_test_module", files=[test_rel], module=module, name=module, detail=module)


def op_new_module(repo: Path, rng: random.Random, rel: Path) -> Change | None:
    """Create a brand-new small module from the fixture pool."""
    available = [name for name in library.NEW_MODULES if not (repo / name).exists()]
    if not available:
        return None
    name = rng.choice(available)
    rel_path = Path(name)
    rel_path.parent.mkdir(parents=True, exist_ok=True)
    (repo / rel_path).write_text(library.NEW_MODULES[name], encoding="utf-8")
    return Change(op="new_module", files=[rel_path], module=rel_path.stem, name=rel_path.stem, detail=rel_path.stem)


def op_update_readme(repo: Path, rng: random.Random, rel: Path) -> Change | None:
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


def op_version_bump(repo: Path, rng: random.Random, rel: Path) -> Change | None:
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

FILE_OPS: dict[str, object] = {
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
    "add_test": op_add_test,
}

META_OPS: dict[str, object] = {
    "new_module": op_new_module,
    "new_test_module": op_new_test_module,
    "update_readme": op_update_readme,
    "version_bump": op_version_bump,
}

FILE_WEIGHTS: dict[str, int] = {
    "add_helper": 16,
    "add_docstring": 10,
    "add_type_hint": 9,
    "add_test": 9,
    "add_constant": 6,
    "add_validation": 6,
    "reorder_imports": 5,
    "cleanup_whitespace": 5,
    "change_default": 5,
    "add_parameter": 5,
    "remove_dead_code": 4,
    "add_logging": 3,
}

META_WEIGHTS: dict[str, int] = {
    "new_module": 2,
    "new_test_module": 2,
    "update_readme": 3,
    "version_bump": 2,
}


def try_file_op(repo: Path, rng: random.Random, op: str, rel: Path) -> Change | None:
    """Attempt one file-level op; returns None when not applicable."""
    return FILE_OPS[op](repo, rng, rel)  # type: ignore[operator]


def try_meta_op(repo: Path, rng: random.Random, op: str) -> Change | None:
    """Attempt one meta-level op."""
    return META_OPS[op](repo, rng, None)  # type: ignore[operator]
