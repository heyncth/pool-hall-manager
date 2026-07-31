"""Git plumbing: stage, commit, push and a compile gate.

Answers the single question: *"how do changes get written into git history?"*
The module knows nothing about how changes are generated.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import timeline  # noqa: E402

AUTHOR_NAME = "Nguyễn Công Thuận Huy"
AUTHOR_EMAIL = "nguyencongthuanhuy@gmail.com"


def compile_ok(path: Path) -> bool:
    """Return True when ``path`` is syntactically valid Python."""
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(path)],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def commit(repo: Path, files: list[Path], message: str, when) -> str:
    """Stage ``files`` and create a commit dated ``when``.

    Returns "ok", "empty" (nothing to commit) or "error".
    """
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    env["GIT_AUTHOR_DATE"] = timeline.git_date(when)
    env["GIT_COMMITTER_DATE"] = timeline.git_date(when)

    for file in files:
        subprocess.run(
            ["git", "-C", str(repo), "add", "--", file.as_posix()],
            env=env, capture_output=True, check=False,
        )

    result = subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", message],
        env=env, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        combined = (result.stdout or "") + (result.stderr or "")
        if "nothing to commit" in combined:
            return "empty"
        print(f"  ! commit failed: {(result.stderr or '').strip()[:200]}")
        return "error"
    return "ok"


def remove(repo: Path, path: str, when) -> str:
    """Remove a tracked path (git rm -r) and commit the deletion."""
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    env["GIT_AUTHOR_DATE"] = timeline.git_date(when)
    env["GIT_COMMITTER_DATE"] = timeline.git_date(when)

    result = subprocess.run(
        ["git", "-C", str(repo), "rm", "-r", "--", path],
        env=env, capture_output=True, check=False,
    )
    if result.returncode != 0:
        print(f"  ! git rm failed: {(result.stderr or '').strip()[:200]}")
        return "error"
    commit_result = subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "refactor: drop legacy Java Swing prototype"],
        env=env, capture_output=True, text=True, check=False,
    )
    if commit_result.returncode != 0:
        return "error"
    return "ok"


def head_short_hash(repo: Path) -> str:
    """Return the short hash of HEAD (empty when there is no commit yet)."""
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def recent_commits(repo: Path, limit: int = 30) -> list[dict]:
    """Return the most recent commit subjects, one dict per commit."""
    result = subprocess.run(
        ["git", "-C", str(repo), "log", f"-{limit}", "--pretty=format:%s"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return []
    return [{"subject": line.strip()} for line in result.stdout.splitlines() if line.strip()]


def recent_files(repo: Path, limit: int = 30) -> list[str]:
    """Return paths touched by the most recent commits (most recent first)."""
    result = subprocess.run(
        ["git", "-C", str(repo), "log", f"-{limit}", "--name-only", "--pretty=format:"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return []
    seen: list[str] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if line and line not in seen:
            seen.append(line)
    return seen


def push(repo: Path) -> bool:
    """Push commits to the configured remote."""
    result = subprocess.run(
        ["git", "-C", str(repo), "push"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        print(f"  ! push failed: {(result.stderr or '').strip()[:200]}")
        return False
    return True
