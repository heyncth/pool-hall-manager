"""Engine self-tests: run on a throwaway git repo, never on the real one."""

from __future__ import annotations

import ast
import random
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import git as vcs  # noqa: E402
import library  # noqa: E402
import main as engine  # noqa: E402
import message  # noqa: E402
import mutation  # noqa: E402
import planner  # noqa: E402
import timeline  # noqa: E402

CORE_SOURCE = '''\
"""Core."""

from __future__ import annotations


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
'''

TEST_CORE = '''\
from poolhall.core import add


def test_add():
    assert add(1, 2) == 3
'''


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "poolhall").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "poolhall" / "__init__.py").write_text('"""Package."""\n', encoding="utf-8")
    (root / "poolhall" / "core.py").write_text(CORE_SOURCE, encoding="utf-8")
    (root / "tests" / "test_core.py").write_text(TEST_CORE, encoding="utf-8")
    _git(root, "init")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "init")
    return root


def test_compile_ok_valid_and_invalid(repo: Path) -> None:
    good = repo / "poolhall" / "core.py"
    bad = repo / "broken.py"
    bad.write_text("def f(:\n", encoding="utf-8")
    assert vcs.compile_ok(good)
    assert not vcs.compile_ok(bad)


def test_compile_ok_catches_future_misplacement(repo: Path) -> None:
    bad = repo / "poolhall" / "late_future.py"
    bad.write_text("from . import core\nfrom __future__ import annotations\n", encoding="utf-8")
    assert not vcs.compile_ok(bad)


def test_reorder_keeps_future_first(repo: Path) -> None:
    target = Path("poolhall") / "core.py"
    source = (repo / target).read_text(encoding="utf-8")
    unsorted = source.replace(
        "from __future__ import annotations",
        "from __future__ import annotations\n\nimport random\nfrom dataclasses import dataclass",
    )
    (repo / target).write_text(unsorted, encoding="utf-8")
    change = mutation.op_reorder_imports(repo, random.Random(1), target)
    assert change is not None
    assert vcs.compile_ok(repo / target)
    result = (repo / target).read_text(encoding="utf-8")
    assert result.index("from __future__") < result.index("from dataclasses")
    assert result.index("from dataclasses") < result.index("import random")


def test_reorder_noop_when_already_sorted(repo: Path) -> None:
    target = Path("poolhall") / "core.py"
    assert mutation.op_reorder_imports(repo, random.Random(1), target) is None


def test_change_default_touches_one_default(repo: Path) -> None:
    target = Path("poolhall") / "twoparams.py"
    (repo / target).write_text(
        '"""M."""\n\n\ndef scale(a: int = 0, b: int = 0) -> int:\n    """Scale."""\n    return a + b\n',
        encoding="utf-8",
    )
    rng = random.Random(7)
    change = mutation.op_change_default(repo, rng, target)
    assert change is not None
    text = (repo / target).read_text(encoding="utf-8")
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef))
    defaults = sorted(d.value for d in node.args.defaults)
    assert defaults == [0, 1], f"exactly one default should change, got {defaults}:\n{text}"


def test_remove_dead_code_removes_unused_constant(repo: Path) -> None:
    target = Path("poolhall") / "core.py"
    text = (repo / target).read_text(encoding="utf-8") + "\n\nDEAD_CONSTANT = 42\nLIVE_CONSTANT = 1\n"
    text += "\ndef use_live() -> int:\n    return LIVE_CONSTANT\n"
    (repo / target).write_text(text, encoding="utf-8")
    for _ in range(10):
        change = mutation.op_remove_dead_code(repo, random.Random(3), target)
        if change is not None and change.name == "DEAD_CONSTANT":
            break
    else:
        pytest.fail("remove_dead_code never picked DEAD_CONSTANT")
    result = (repo / target).read_text(encoding="utf-8")
    assert "DEAD_CONSTANT" not in result
    assert "LIVE_CONSTANT" in result


def test_rollback_restores_snapshot(repo: Path) -> None:
    target = Path("poolhall") / "core.py"
    snapshot = {target: (repo / target).read_text(encoding="utf-8")}
    change = mutation.op_add_helper(repo, random.Random(1), target)
    assert change is not None
    assert (repo / target).read_text(encoding="utf-8") != snapshot[target]
    engine._rollback(repo, snapshot, change)
    assert (repo / target).read_text(encoding="utf-8") == snapshot[target]


def test_reset_index_clears_staging(repo: Path) -> None:
    scratch = repo / "poolhall" / "scratch.py"
    scratch.write_text("X = 1\n", encoding="utf-8")
    _git(repo, "add", "--", "poolhall/scratch.py")
    staged = subprocess.run(
        ["git", "-C", str(repo), "diff", "--cached", "--name-only"],
        capture_output=True, text=True, check=True,
    ).stdout
    assert "scratch.py" in staged
    vcs.reset_index(repo)
    staged = subprocess.run(
        ["git", "-C", str(repo), "diff", "--cached", "--name-only"],
        capture_output=True, text=True, check=True,
    ).stdout
    assert staged.strip() == ""


def test_gate_rejects_broken_file(repo: Path) -> None:
    target = Path("poolhall") / "broken.py"
    (repo / target).write_text("def f(:\n", encoding="utf-8")
    change = mutation.Change(op="test", files=[target])
    assert engine._gate(repo, change, "compile") is False


def test_gate_accepts_valid_change(repo: Path) -> None:
    target = Path("poolhall") / "core.py"
    change = mutation.Change(op="test", files=[target])
    assert engine._gate(repo, change, "compile") is True


def test_helper_snippets_compile() -> None:
    snippets = library.helper_snippets() + library.validator_snippets()
    names = [name for name, _ in snippets]
    assert len(names) == len(set(names))
    for _, source in snippets:
        compile(source, "<snippet>", "exec")


def test_constant_snippets_prefixed() -> None:
    snippets = library.constant_snippets("billing")
    assert all(name.startswith("BILLING_") for name, _ in snippets)


def test_test_source_compiles() -> None:
    funcs = [
        {"name": "no_args", "args": [], "kwonly": [], "has_vararg": False},
        {"name": "needs_args", "args": ["tables"], "kwonly": [], "has_vararg": False},
    ]
    source = mutation._test_source("core", funcs)
    compile(source, "<test>", "exec")
    assert "def test_no_args():" in source
    assert "assert callable(mod.needs_args)" in source


def test_add_type_hint_fires(repo: Path) -> None:
    target = Path("poolhall") / "untyped.py"
    (repo / target).write_text(
        '"""U."""\n\n\ndef double(count):\n    """Double count."""\n    return count * 2\n',
        encoding="utf-8",
    )
    change = mutation.op_add_type_hint(repo, random.Random(2), target)
    assert change is not None
    assert vcs.compile_ok(repo / target)
    assert "count: int" in (repo / target).read_text(encoding="utf-8")


def test_add_parameter_fires(repo: Path) -> None:
    target = Path("poolhall") / "plain.py"
    (repo / target).write_text(
        '"""P."""\n\n\ndef total(amount):\n    """Total amount."""\n    return amount\n',
        encoding="utf-8",
    )
    change = mutation.op_add_parameter(repo, random.Random(2), target)
    assert change is not None
    assert vcs.compile_ok(repo / target)


def test_signature_ops_skip_tests(repo: Path) -> None:
    target = Path("tests") / "test_core.py"
    rng = random.Random(1)
    assert mutation.op_add_type_hint(repo, rng, target) is None
    assert mutation.op_add_parameter(repo, rng, target) is None
    assert mutation.op_change_default(repo, rng, target) is None
    assert mutation.op_add_docstring(repo, rng, target) is None


def test_message_unknown_op_falls_back() -> None:
    assert message.make(random.Random(1), "nope", "mod", "", "", None, []) == "chore: update mod"
    assert message.type_of("nope") == "chore"


def test_late_messages_go_casual() -> None:
    rng = random.Random(2)
    results = [message.make(rng, "add_helper", "m", "x", "x", None, [], late=True) for _ in range(60)]
    bare = [m for m in results if ":" not in m]
    assert len(bare) >= 5, "late-evening casual pool never fired"
    assert all(m in message.CASUAL for m in bare)


def test_bodies_occasionally_appear() -> None:
    rng = random.Random(9)
    results = [message.make(rng, "add_helper", "m", "x", "x", None, [], late=False) for _ in range(80)]
    assert sum(1 for m in results if "\n\n" in m) >= 3


def test_followup_commits_when_whitespace_exists(repo: Path, monkeypatch) -> None:
    monkeypatch.setattr(engine, "FOLLOWUP_P", 1.0)
    target = Path("poolhall") / "messy.py"
    (repo / target).write_text(CORE_SOURCE + "\nZ = 1   \n\n\n\n", encoding="utf-8")
    at = datetime(2026, 1, 10, 10, 0, tzinfo=timeline.LOCAL_TZ)
    out = engine._followup(repo, random.Random(3), target, at, "compile", [])
    assert out is not None, "expected a real whitespace fixup"
    subject, when, change = out
    assert subject.startswith(("style:", "chore:"))
    assert when.date() == at.date()
    assert 2 <= (when - at).total_seconds() <= 15 * 60
    log = subprocess.run(
        ["git", "-C", str(repo), "log", "-1", "--pretty=format:%s"],
        capture_output=True, text=True, check=True,
    ).stdout
    assert log == subject


def test_followup_refuses_clean_file(repo: Path, monkeypatch) -> None:
    monkeypatch.setattr(engine, "FOLLOWUP_P", 1.0)
    target = Path("poolhall") / "core.py"
    at = datetime(2026, 1, 10, 10, 0, tzinfo=timeline.LOCAL_TZ)
    assert engine._followup(repo, random.Random(3), target, at, "compile", []) is None
    status = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"],
        capture_output=True, text=True, check=True,
    ).stdout
    assert status.strip() == ""


def test_timeline_deterministic() -> None:
    day = timeline.local_now()
    first = timeline.commit_times(random.Random(5), 4, day)
    second = timeline.commit_times(random.Random(5), 4, day)
    assert first == second
    assert all(t.tzinfo is not None for t in first)


def test_year_statistics() -> None:
    """Golden ranges: right-skewed year with rare bright spikes (B3 targets)."""
    from datetime import timedelta

    rng = random.Random(42)
    day0 = datetime(2026, 1, 1, tzinfo=timeline.LOCAL_TZ)
    counts = [timeline.pick_commit_count(rng, day0 + timedelta(days=i)) for i in range(365)]
    assert 10 <= sum(1 for c in counts if c >= 15) <= 45, "bright (Q4) days out of range"
    assert sum(1 for c in counts if 0 < c <= 4) >= 120, "low days must dominate"
    assert 90 <= counts.count(0) <= 170, "zero days out of range"
    assert max(counts) >= 15, "no heavy-tail spike"
    assert 800 <= sum(counts) <= 1600, "annual total out of range"


def _state_runs(year: int) -> list[tuple[str, int]]:
    days = timeline.year_days(year)
    runs: list[tuple[str, int]] = []
    for d in sorted(days):
        state = days[d][0]
        if runs and runs[-1][0] == state:
            runs[-1] = (state, runs[-1][1] + 1)
        else:
            runs.append((state, 1))
    return runs


def test_crunch_clusters_bounded_and_dipped() -> None:
    """Crunch = 2-5 day clusters, always followed by a rest dip (burnout)."""
    runs = _state_runs(2026)
    crunch_runs = [(i, n) for i, (s, n) in enumerate(runs) if s == "crunch"]
    assert len(crunch_runs) >= 3, "year needs several crunch clusters"
    for index, length in crunch_runs:
        assert 2 <= length <= 5
        assert runs[index + 1][0] in ("rest",) or index + 1 == len(runs) - 1, \
            "crunch must end in a rest dip"


def test_vacation_gap_exists() -> None:
    runs = _state_runs(2026)
    assert any(s == "rest" and n >= 5 for s, n in runs), "no vacation block (5+ days)"


def test_commit_times_session_shape() -> None:
    """Sessions respect circadian rules: sleep gap, meal troughs, second entropy."""
    rng = random.Random(11)
    day = datetime(2026, 3, 4, tzinfo=timeline.LOCAL_TZ)
    times: list[datetime] = []
    for count in (1, 3, 7, 14, 40):
        times.extend(timeline.commit_times(rng, count, day))
    hours = [t.hour for t in times]
    assert not any(0 <= h <= 7 for h in hours), "commits inside the sleep window"
    assert not any(h in (12, 13, 17, 18, 19) for h in hours), "commits inside meal troughs"
    assert max(times).hour <= 23
    assert max(t.minute for t in times if t.hour == 23) <= 59
    assert len({t.second for t in times}) >= 20, "seconds not random (cron fingerprint)"


def test_peaks_avoid_troughs() -> None:
    for peak in timeline.PEAKS:
        for trough in timeline.TROUGHS:
            assert peak[1] <= trough[0] or peak[0] >= trough[1]


def test_commit_backdates_author(repo: Path) -> None:
    when = datetime(2020, 1, 15, 10, 30, tzinfo=timeline.LOCAL_TZ)
    target = repo / "poolhall" / "newmod.py"
    target.write_text("Y = 2\n", encoding="utf-8")
    result = vcs.commit(repo, [Path("poolhall/newmod.py")], "feat: add newmod", when)
    assert result == "ok"
    log = subprocess.run(
        ["git", "-C", str(repo), "log", "-1", "--pretty=format:%ad", "--date=iso"],
        capture_output=True, text=True, check=True,
    ).stdout
    assert log.startswith("2020-01-15")


def test_commit_missing_file_returns_error(repo: Path) -> None:
    when = datetime.now(tz=timeline.LOCAL_TZ)
    result = vcs.commit(repo, [Path("poolhall/nope.py")], "chore: nothing", when)
    assert result in ("empty", "error")


def _log_field(repo: Path, field: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "log", "-1", f"--pretty=format:%{field}", "--date=iso"],
        capture_output=True, text=True, check=True,
    ).stdout


def test_committer_skew_when_supplied(repo: Path) -> None:
    when = datetime(2020, 1, 15, 10, 30, tzinfo=timeline.LOCAL_TZ)
    skewed = when + timedelta(hours=5)
    (repo / "poolhall" / "newmod.py").write_text("Y = 3\n", encoding="utf-8")
    result = vcs.commit(repo, [Path("poolhall/newmod.py")], "feat: add newmod", when, committer_when=skewed)
    assert result == "ok"
    assert _log_field(repo, "ad").startswith("2020-01-15 10:30")
    assert _log_field(repo, "cd").startswith("2020-01-15 15:30")


def test_branch_merge_delete_cycle(repo: Path) -> None:
    base = vcs.current_branch(repo)
    assert vcs.create_branch(repo, "feature/polish")
    assert vcs.current_branch(repo) == "feature/polish"
    (repo / "poolhall" / "branched.py").write_text("B = 1\n", encoding="utf-8")
    when = datetime(2020, 1, 15, 11, 0, tzinfo=timeline.LOCAL_TZ)
    assert vcs.commit(repo, [Path("poolhall/branched.py")], "feat: branched work", when) == "ok"
    merge_at = when + timedelta(minutes=7)
    assert vcs.checkout(repo, base)
    assert vcs.merge_no_ff(repo, "feature/polish", "Merge branch 'feature/polish'", merge_at) == "ok"
    vcs.delete_branch(repo, "feature/polish")
    vcs.checkout(repo, base)
    parents = subprocess.run(
        ["git", "-C", str(repo), "log", "-1", "--pretty=format:%P"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    assert len(parents) == 2, "merge must be a real merge commit"
    branches = subprocess.run(
        ["git", "-C", str(repo), "branch", "--format=%(refname:short)"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    assert "feature/polish" not in branches
    assert vcs.current_branch(repo) == base


def test_forced_branch_cleanup_merges_stranded_work(repo: Path) -> None:
    base = vcs.current_branch(repo)
    assert vcs.create_branch(repo, "feature/helpers")
    (repo / "poolhall" / "stranded.py").write_text("S = 1\n", encoding="utf-8")
    when = datetime(2020, 1, 15, 12, 0, tzinfo=timeline.LOCAL_TZ)
    assert vcs.commit(repo, [Path("poolhall/stranded.py")], "feat: stranded work", when) == "ok"
    assert engine._merge_branch(repo, "feature/helpers", base, when + timedelta(minutes=2))
    assert vcs.current_branch(repo) == base
    branches = subprocess.run(
        ["git", "-C", str(repo), "branch", "--format=%(refname:short)"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    assert "feature/helpers" not in branches
    assert (repo / "poolhall" / "stranded.py").exists(), "stranded work must survive the merge"


def test_revert_commit_restores_content(repo: Path) -> None:
    target = repo / "poolhall" / "core.py"
    target.write_text(CORE_SOURCE + "EXTRA = 1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "feat: add EXTRA")
    sha = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    when = datetime(2020, 1, 16, 9, 0, tzinfo=timeline.LOCAL_TZ)
    assert vcs.revert_commit(repo, sha, when) == "ok"
    change = mutation.Change(op="revert", files=[Path("poolhall/core.py")])
    assert engine._gate(repo, change, "compile")
    assert vcs.commit_revert(repo, sha, when) == "ok"
    assert "EXTRA" not in target.read_text(encoding="utf-8")
    subject = _log_field(repo, "s")
    assert subject.startswith('Revert "feat: add EXTRA"')


def test_tweak_literal_nudges_constant(repo: Path) -> None:
    target = repo / "poolhall" / "limits.py"
    target.write_text("RETRY_LIMIT = 10\n", encoding="utf-8")
    change = mutation.op_tweak_literal(repo, random.Random(4), Path("poolhall/limits.py"))
    assert change is not None and change.op == "tweak_literal"
    source = target.read_text(encoding="utf-8")
    value = ast.literal_eval(source.split("=", 1)[1].strip())
    assert isinstance(value, int) and value != 10
    assert vcs.compile_ok(target)


def test_remove_dead_code_drops_paired_test(repo: Path) -> None:
    (repo / "poolhall" / "helpers_mod.py").write_text(
        "def _orphan(x):\n    return x + 1\n", encoding="utf-8"
    )
    (repo / "tests" / "test_helpers_mod.py").write_text(
        "import poolhall.aux as mod\n\n\n"
        "def test__orphan():\n"
        "    assert callable(mod._orphan)\n",
        encoding="utf-8",
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "feat: aux + orphan test")
    change = mutation.op_remove_dead_code(repo, random.Random(3), Path("poolhall/helpers_mod.py"))
    assert change is not None, "test-only referenced helper must be removable in a pair"
    assert change.files == [Path("poolhall/helpers_mod.py"), Path("tests/test_helpers_mod.py")]
    assert "_orphan" not in (repo / "poolhall" / "helpers_mod.py").read_text(encoding="utf-8")
    assert "def test__orphan" not in (repo / "tests" / "test_helpers_mod.py").read_text(encoding="utf-8")
    assert mutation.op_remove_dead_code(repo, random.Random(3), Path("poolhall/helpers_mod.py")) is None


def test_remove_dead_code_keeps_helper_used_by_unrelated_test(repo: Path) -> None:
    (repo / "poolhall" / "helpers_mod.py").write_text(
        "def _shared(x):\n    return x\n", encoding="utf-8"
    )
    (repo / "tests" / "test_helpers_mod.py").write_text(
        "from poolhall.aux import _shared\n\n\n"
        "def test_something():\n"
        "    assert _shared(1) == 1\n",
        encoding="utf-8",
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "feat: aux + shared test")
    assert mutation.op_remove_dead_code(repo, random.Random(3), Path("poolhall/helpers_mod.py")) is None


def test_plan_hints_companion_test(repo: Path) -> None:
    (repo / "poolhall" / "tables.py").write_text(
        "def total(xs):\n    return sum(xs)\n", encoding="utf-8"
    )
    (repo / "tests" / "test_tables.py").write_text(
        '"""Tests for the tables module."""\n', encoding="utf-8"
    )
    rng = random.Random(5)
    change = planner.plan(rng, repo, [], [], [], file_hint="tests/test_tables.py")
    assert change is not None and change.op == "add_test"
    assert change.files == [Path("tests/test_tables.py")]


def test_plan_hint_on_missing_file_falls_back(repo: Path) -> None:
    rng = random.Random(5)
    change = planner.plan(rng, repo, [], [], [], file_hint="tests/nope.py")
    assert change is None or isinstance(change, mutation.Change)
