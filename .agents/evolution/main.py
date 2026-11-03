"""Orchestrator for the Repository Evolution Engine.

Pipeline: timeline -> planner -> mutation -> compile gate -> message -> git
Each module answers exactly one question; this file only wires them together.
"""

from __future__ import annotations

import argparse
import random
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import bootstrap  # noqa: E402
import git  # noqa: E402
import message  # noqa: E402
import mutation  # noqa: E402
import planner  # noqa: E402
import timeline  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ZONE_MARKER = Path("poolhall") / "__init__.py"

# Self-correction commits: opportunistic, only when a real matching change
# exists (semantic-diff alignment), 2-15 minutes after the parent commit.
FOLLOWUP_P = 0.10
FOLLOWUP_OPS = ("cleanup_whitespace",)
FOLLOWUP_MESSAGES = ("style: adjust spacing", "style: tidy spacing", "chore: fixup formatting")

# Human history topology (see plan B8-B10).
COMMIT_SKEW_P = 0.10       # CommitterDate 2min..3days after AuthorDate (amend/rebase)
BRANCH_P = 0.15            # chance per commit-slot to start a feature branch
REVERT_P = 0.03            # chance per run to land a revert commit
BRANCH_SLUGS = ("polish", "receipt-tweaks", "helpers", "table-utils", "readme-pass")


def _parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timeline.LOCAL_TZ)


def _derive_seed(day: datetime, head_hash: str, explicit: int | None) -> int:
    if explicit is not None:
        return explicit
    return (day.toordinal() << 8) ^ int((head_hash or "0")[:8], 16)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Repository Evolution Engine")
    parser.add_argument("--repo", default=str(REPO_ROOT), help="repository root (default: this repo)")
    parser.add_argument("--date", default=None, help="simulate a specific day, YYYY-MM-DD")
    parser.add_argument("--seed", type=int, default=None, help="override the PRNG seed")
    parser.add_argument("--max-commits", type=int, default=None, help="force a commit count")
    parser.add_argument("--dry-run", action="store_true", help="plan changes without committing")
    parser.add_argument("--no-push", action="store_true", help="do not push after committing")
    parser.add_argument("--gate", choices=("tests", "compile"), default="tests", help="validation before commit: full test suite or syntax only")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    day = _parse_date(args.date) if args.date else timeline.local_now()
    head_hash = git.head_short_hash(repo)
    seed = _derive_seed(day, head_hash, args.seed)
    rng = random.Random(seed)

    if not (repo / ZONE_MARKER).exists():
        if args.dry_run:
            print("  bootstrap would run (no poolhall/ package yet)")
        else:
            print("  bootstrapping ported project...")
            bootstrap.run(repo, day)
            head_hash = git.head_short_hash(repo)

    count = args.max_commits if args.max_commits is not None else timeline.pick_commit_count(rng, day)
    times = timeline.commit_times(rng, count, day)
    print(f"  day {day.date().isoformat()} -> {count} commits (seed={seed})")

    recent_commits = git.recent_commits(repo, 30)
    recent_messages = [c["subject"] for c in recent_commits]
    recent_types = [m.split("(")[0].split(":")[0].strip() for m in recent_messages]
    recent_files = git.recent_files(repo, 30)
    touched_today: list[str] = []
    companion_hint: str | None = None
    made = 0
    base_branch = git.current_branch(repo)
    branch_name: str | None = None
    branch_commits = 0
    branch_target = 0
    last_when = times[-1] if times else timeline.local_now()

    for when in times:
        last_when = when
        if not args.dry_run and branch_name is None and made > 0 and rng.random() < BRANCH_P:
            candidate = f"feature/{rng.choice(BRANCH_SLUGS)}"
            if git.create_branch(repo, candidate):
                branch_name = candidate
                branch_commits = 0
                branch_target = rng.randint(1, 3)
        snapshot = _snapshot(repo)
        hint, companion_hint = companion_hint, None
        change = None
        for _ in range(4):
            change = planner.plan(rng, repo, recent_files, recent_types, touched_today, file_hint=hint)
            if change is not None and _gate(repo, change, args.gate):
                break
            if change is not None:
                _rollback(repo, snapshot, change)
            change = None
        if change is None:
            continue
        subject = message.make(rng, change.op, change.module, change.name, change.detail, change.version, recent_messages, late=when.hour >= 20)
        if args.dry_run:
            print(f"  [dry-run] {when:%H:%M} {change.op:<18} {subject}  ({', '.join(str(f) for f in change.files)})")
            _rollback(repo, snapshot, change)  # dry-run must not touch the tree
            made += 1
            continue
        committer_when = when
        if rng.random() < COMMIT_SKEW_P:
            committer_when = when + timedelta(minutes=rng.randint(2, 60 * 72))
        result = git.commit(repo, change.files, subject, when, committer_when=committer_when)
        if result != "ok":
            _rollback(repo, snapshot, change)
            git.reset_index(repo)
            continue
        print(f"  {when:%H:%M} {subject}")
        made += 1
        if branch_name is not None:
            branch_commits += 1
        if change.op in ("add_helper", "add_constant", "add_validation", "add_type_hint") and change.module:
            test_rel = mutation.test_file_for(change.module)
            if (repo / test_rel).exists():
                companion_hint = str(test_rel)
        recent_messages = recent_messages[-29:] + [subject]
        recent_types = recent_types[-9:] + [message.type_of(change.op)]
        touched_today.extend(str(f) for f in change.files)
        recent_files = [f for f in recent_files if f not in touched_today] + touched_today

        followup = _followup(repo, rng, change.files[0], when, args.gate, recent_messages)
        if followup is not None:
            fu_subject, fu_at, fu_change = followup
            print(f"  {fu_at:%H:%M} {fu_subject}")
            made += 1
            recent_messages = recent_messages[-29:] + [fu_subject]
            recent_types = recent_types[-9:] + [message.type_of(fu_change.op)]
            touched_today.extend(str(f) for f in fu_change.files)
            recent_files = [f for f in recent_files if f not in touched_today] + touched_today

        if branch_name is not None and branch_commits >= branch_target:
            at = when + timedelta(minutes=rng.randint(1, 10))
            if at.date() != when.date():
                at = when
            if _merge_branch(repo, branch_name, base_branch, at):
                branch_name = None

    if branch_name is not None and not args.dry_run:
        # never strand commits off the base branch, whatever happened above
        at = max(timeline.local_now(), last_when + timedelta(minutes=1))
        _merge_branch(repo, branch_name, base_branch, at)
        branch_name = None

    if made and not args.dry_run and rng.random() < REVERT_P:
        if _revert(repo, rng, last_when + timedelta(minutes=3), args.gate):
            made += 1

    print(f"  {made}/{count} committed")
    if made and not args.dry_run and not args.no_push:
        git.push(repo)
    return 0


def _merge_branch(repo: Path, branch_name: str, base_branch: str, at: datetime) -> bool:
    """Merge a feature branch back and restore the base branch."""
    if not git.checkout(repo, base_branch):
        return False  # leave it open; end-of-run cleanup retries
    if git.merge_no_ff(repo, branch_name, f"Merge branch '{branch_name}'", at) != "ok":
        return False  # leave it open; end-of-run cleanup retries
    git.delete_branch(repo, branch_name)
    return True


def _staged_files(repo: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(repo), "diff", "--cached", "--name-only"],
        capture_output=True, text=True, check=False,
    )
    return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def _revert(repo: Path, rng: random.Random, at: datetime, gate_mode: str) -> bool:
    """Land one backdated revert of a recent commit; gated like any change."""
    candidates = git.recent_revertable(repo, 6)
    if not candidates:
        return False
    sha, _subject = rng.choice(candidates)
    snapshot = _snapshot(repo)
    if git.revert_commit(repo, sha, at) != "ok":
        return False
    zone = [
        rel for rel in _staged_files(repo)
        if (len(rel.parts) > 1 and rel.parts[0] in mutation.MODULE_DIRS)
        or rel.name in mutation.ROOT_FILES
    ]
    if not zone:
        git.reset_index(repo)
        _rollback(repo, snapshot, mutation.Change(op="revert", files=[]))
        return False
    change = mutation.Change(op="revert", files=zone)
    if not _gate(repo, change, gate_mode):
        _rollback(repo, snapshot, change)
        git.reset_index(repo)
        return False
    if git.commit_revert(repo, sha, at) != "ok":
        _rollback(repo, snapshot, change)
        git.reset_index(repo)
        return False
    print(f"  {at:%H:%M} Revert \"{_subject}\"")
    return True


def _followup(repo: Path, rng: random.Random, rel: Path, when: datetime, gate_mode: str, history: list[str]) -> tuple[str, datetime, mutation.Change] | None:
    """Attempt an opportunistic fixup commit right after a successful parent."""
    if rng.random() >= FOLLOWUP_P:
        return None
    snapshot = _snapshot(repo)
    change = None
    for op in FOLLOWUP_OPS:
        change = mutation.try_file_op(repo, rng, op, rel)
        if change is not None:
            break
    if change is None:
        return None  # nothing real to correct -> never fake a diff
    if not _gate(repo, change, gate_mode):
        _rollback(repo, snapshot, change)
        return None
    at = when + timedelta(minutes=rng.randint(2, 15))
    if at.date() != when.date():
        _rollback(repo, snapshot, change)
        return None
    options = [m for m in FOLLOWUP_MESSAGES if m not in history] or list(FOLLOWUP_MESSAGES)
    subject = rng.choice(options)
    if git.commit(repo, change.files, subject, at) != "ok":
        _rollback(repo, snapshot, change)
        git.reset_index(repo)
        return None
    return subject, at, change


def _gate(repo: Path, change: mutation.Change, mode: str) -> bool:
    """Validate a mutation: every changed .py must compile; tests gate also runs pytest."""
    for rel in change.files:
        if rel.suffix != ".py":
            continue
        path = repo / rel
        if not path.exists():
            return False
        if not git.compile_ok(path):
            print(f"  ! compile gate failed for {rel}, skipping")
            return False
    if mode == "tests" and not _tests_pass(repo):
        print(f"  ! tests gate failed for {change.op}, rolling back")
        return False
    return True


def _tests_pass(repo: Path) -> bool:
    """Run the repository's zone test suite; True when it is green."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider", "tests"],
        cwd=str(repo), capture_output=True, text=True,
    )
    return result.returncode == 0


def _snapshot(repo: Path) -> dict:
    """Snapshot all zone file contents so failed mutations can be rolled back."""
    snap: dict = {}
    for rel in mutation.zone_py_files(repo):
        path = repo / rel
        if path.exists():
            snap[rel] = path.read_text(encoding="utf-8")
    for rel in (Path("README.md"), Path("pyproject.toml")):
        path = repo / rel
        if path.exists():
            snap[rel] = path.read_text(encoding="utf-8")
    return snap


def _rollback(repo: Path, snapshot: dict, change: mutation.Change) -> None:
    """Undo a mutation that failed the compile gate (spec: fail -> rollback)."""
    for rel in change.files:
        path = repo / rel
        if rel not in snapshot and path.exists():
            path.unlink()  # newly created file
    for rel, content in snapshot.items():
        (repo / rel).write_text(content, encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
