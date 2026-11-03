"""Git plumbing: stage, commit, push and a compile gate.

Answers the single question: *"how do changes get written into git history?"*
The module knows nothing about how changes are generated.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))

import timeline  # noqa: E402

AUTHOR_NAME = "Nguyễn Công Thuận Huy"
AUTHOR_EMAIL = "nguyencongthuanhuy@gmail.com"


def _env(when, committer_when=None) -> dict[str, str]:
    """Git environment with the engine's author identity and dates."""
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    if when is not None:
        env["GIT_AUTHOR_DATE"] = timeline.git_date(when)
    if committer_when is not None:
        env["GIT_COMMITTER_DATE"] = timeline.git_date(committer_when)
    elif when is not None:
        env["GIT_COMMITTER_DATE"] = timeline.git_date(when)
    return env


def compile_ok(path: Path) -> bool:
    """Return True when ``path`` is syntactically valid Python."""
    try:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    except (SyntaxError, ValueError, OSError):
        return False
    return True


def reset_index(repo: Path) -> None:
    """Unstage everything, leaving the worktree intact."""
    subprocess.run(
        ["git", "-C", str(repo), "reset"],
        capture_output=True, check=False,
    )


def commit(repo: Path, files: list[Path], message: str, when, committer_when=None) -> str:
    """Stage ``files`` and create a commit dated ``when``.

    ``committer_when`` simulates amend/rebase (CommitterDate later than
    AuthorDate). Returns "ok", "empty" (nothing to commit) or "error".
    """
    env = _env(when, committer_when)

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
    env = _env(when)

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


def current_branch(repo: Path) -> str:
    """Name of the checked-out branch (falls back to ``main``)."""
    result = subprocess.run(
        ["git", "-C", str(repo), "branch", "--show-current"],
        capture_output=True, text=True, check=False,
    )
    name = result.stdout.strip()
    return name or "main"


def create_branch(repo: Path, name: str) -> bool:
    """Create and check out ``name`` from HEAD."""
    result = subprocess.run(
        ["git", "-C", str(repo), "checkout", "-b", name],
        capture_output=True, text=True, check=False,
    )
    return result.returncode == 0


def checkout(repo: Path, name: str) -> bool:
    """Check out ``name``."""
    result = subprocess.run(
        ["git", "-C", str(repo), "checkout", name],
        capture_output=True, text=True, check=False,
    )
    return result.returncode == 0


def delete_branch(repo: Path, name: str) -> bool:
    """Delete the local branch ``name`` (-d: only when merged)."""
    result = subprocess.run(
        ["git", "-C", str(repo), "branch", "-d", name],
        capture_output=True, text=True, check=False,
    )
    return result.returncode == 0


def merge_no_ff(repo: Path, name: str, message: str, when) -> str:
    """Merge ``name`` into the current branch with a backdated merge commit."""
    result = subprocess.run(
        ["git", "-C", str(repo), "merge", "--no-ff", "-m", message, name],
        env=_env(when), capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        print(f"  ! merge failed: {(result.stderr or '').strip()[:200]}")
        return "error"
    return "ok"


def revert_commit(repo: Path, sha: str, when) -> str:
    """Apply the reverse of ``sha`` to the worktree without committing.

    Returns "ok" when the revert staged cleanly (caller gates and commits or
    rolls back), "error" otherwise (state fully quit, tree untouched).
    """
    env = _env(when)
    result = subprocess.run(
        ["git", "-C", str(repo), "revert", "--no-commit", sha],
        env=env, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        subprocess.run(["git", "-C", str(repo), "revert", "--quit"],
                       env=env, capture_output=True, check=False)
        return "error"
    return "ok"


def commit_revert(repo: Path, sha: str, when, committer_when=None) -> str:
    """Commit the staged revert with the engine identity and dates."""
    subject_result = subprocess.run(
        ["git", "-C", str(repo), "log", "-1", "--pretty=format:%s", sha],
        capture_output=True, text=True, check=False,
    )
    subject = subject_result.stdout.strip() or "change"
    env = _env(when, committer_when)
    result = subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", f'Revert "{subject}"'],
        env=env, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        combined = (result.stdout or "") + (result.stderr or "")
        if "nothing to commit" in combined:
            return "empty"
        print(f"  ! revert commit failed: {(result.stderr or '').strip()[:200]}")
        return "error"
    return "ok"


def recent_revertable(repo: Path, limit: int = 5) -> list[tuple[str, str]]:
    """Recent non-merge, non-revert commits as (sha, subject)."""
    result = subprocess.run(
        ["git", "-C", str(repo), "log", f"-{limit}", "--no-merges", "--pretty=format:%H %s"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return []
    out: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        sha, _, subject = line.partition(" ")
        if subject and not subject.startswith("Revert "):
            out.append((sha, subject))
    return out


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
