#!/usr/bin/env python3
"""
Repo Cleaner: reports & (optionally) removes unused Python files and clutter.

What it does
------------
- Walks the repo import graph starting from entry points (main.py, gui.py).
- Lists local .py files that look "unreachable" (not imported from entry points).
- Suggests archiving large artifacts in data/.
- Cleans __pycache__ and *.pyc.

Safety first
------------
- Protects common package files and dev folders by default:
  * core/__init__.py, features/__init__.py, tools/repo_cleaner.py
  * Any __init__.py (package markers)
  * Everything under tests/, scripts/, tools/ (unless --aggressive)

Usage
-----
  python tools/repo_cleaner.py --report          # dry run (recommended first)
  python tools/repo_cleaner.py --apply           # perform cleanup
  python tools/repo_cleaner.py --report --aggressive
  python tools/repo_cleaner.py --apply  --aggressive

Notes
-----
- This script uses plain file operations, not `git mv/rm`. After apply, run `git add -A`.
"""

from __future__ import annotations
import ast
import argparse
from pathlib import Path
import shutil
import sys

# ---- CONFIG ----
# Where this script lives: <repo>/tools/repo_cleaner.py
REPO_ROOT = Path(__file__).resolve().parents[1]

# Entry points that define "live" code
ENTRY_POINTS = [
    REPO_ROOT / "main.py",
    REPO_ROOT / "gui.py",
]

# Folders to scan for local modules
SOURCE_DIRS = [
    REPO_ROOT / "core",
    REPO_ROOT / "features",
    REPO_ROOT,  # include top-level modules (preferences.py, etc.)
]

# Folders/files never touched by the cleaner
EXCLUDE_DIRS = {
    REPO_ROOT / ".venv",
    REPO_ROOT / "venv",
    REPO_ROOT / "Team Data",
    REPO_ROOT / "WeatherDashboard.egg-info",
    REPO_ROOT / ".git",
    REPO_ROOT / ".mypy_cache",
    REPO_ROOT / ".pytest_cache",
    REPO_ROOT / "dist",
    REPO_ROOT / "build",
}

# Folders protected from deletion unless --aggressive
PROTECT_DIRS = {
    REPO_ROOT / "tests",
    REPO_ROOT / "scripts",
    REPO_ROOT / "tools",
}

# Files protected from deletion always
PROTECT_FILES = {
    REPO_ROOT / "core" / "__init__.py",
    REPO_ROOT / "features" / "__init__.py",
    REPO_ROOT / "tools" / "repo_cleaner.py",
}

# By default, protect ALL __init__.py (unless --aggressive)
PROTECT_ALL_INIT = True

# Patterns (by name) to suggest deletion if unreachable
LIKELY_TRASH_NAMES = {"README.md.save", ".DS_Store", "scheduler.bak.py", "MAINFEST.in"}

ARCHIVE_DIR = REPO_ROOT / "data" / "archive"

# ---- helpers ----

def is_under(path: Path, roots: list[Path] | set[Path]) -> bool:
    p = path.resolve()
    return any(str(p).startswith(str(r.resolve())) for r in roots)

def iter_local_py_files() -> set[Path]:
    files = set()
    for root in SOURCE_DIRS:
        if not root.exists():
            continue
        for p in root.rglob("*.py"):
            if any(str(p).startswith(str(ed)) for ed in EXCLUDE_DIRS):
                continue
            files.add(p.resolve())
    return files

def parse_imports(py_file: Path) -> set[str]:
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
    except Exception:
        # fall back to latin-1 if needed
        try:
            tree = ast.parse(py_file.read_text(encoding="latin-1"))
        except Exception:
            return set()

    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.add(node.module)
    return mods

def resolve_local_module(mod: str) -> Path | None:
    """
    Try to resolve a module name like 'core.weather_api' to a local file.
    Only returns a path if it exists in SOURCE_DIRS.
    """
    # Try module.py
    candidate = REPO_ROOT / (mod.replace(".", "/") + ".py")
    if candidate.exists() and is_under(candidate, SOURCE_DIRS):
        return candidate.resolve()

    # Try package/__init__.py
    candidate = REPO_ROOT / mod.replace(".", "/") / "__init__.py"
    if candidate.exists() and is_under(candidate, SOURCE_DIRS):
        return candidate.resolve()

    return None

def build_reachable() -> set[Path]:
    reachable = set()
    queue = []

    # seed with entry points + package inits
    for ep in ENTRY_POINTS:
        if ep.exists():
            reachable.add(ep.resolve())
            queue.append(ep.resolve())

    while queue:
        current = queue.pop()
        for mod in parse_imports(current):
            loc = resolve_local_module(mod)
            if loc and loc not in reachable:
                reachable.add(loc)
                queue.append(loc)

    return reachable

def find_large_artifacts() -> list[Path]:
    candidates = []
    data_root = REPO_ROOT / "data"
    if data_root.exists():
        for p in data_root.glob("*"):
            if p.is_file() and p.suffix.lower() in {".db", ".sqlite", ".pkl"}:
                candidates.append(p.resolve())
    return candidates

def delete_pycache_and_pyc():
    removed = []
    for p in REPO_ROOT.rglob("__pycache__"):
        if any(str(p).startswith(str(ed)) for ed in EXCLUDE_DIRS):
            continue
        try:
            shutil.rmtree(p)
            removed.append(p)
        except Exception:
            pass
    for p in REPO_ROOT.rglob("*.pyc"):
        if any(str(p).startswith(str(ed)) for ed in EXCLUDE_DIRS):
            continue
        try:
            p.unlink()
            removed.append(p)
        except Exception:
            pass
    return removed

def prune_unreachable(unreachable: list[Path], aggressive: bool) -> tuple[list[Path], list[Path]]:
    """
    Remove protected files/dirs from the unreachable-deletion list.
    Returns (to_delete, protected_list)
    """
    to_delete = []
    protected = []

    for p in unreachable:
        # Always protect explicit files
        if p in PROTECT_FILES:
            protected.append(p); continue

        # Protect dirs unless aggressive
        if not aggressive and is_under(p, PROTECT_DIRS):
            protected.append(p); continue

        # Protect __init__.py unless aggressive
        if not aggressive and p.name == "__init__.py":
            protected.append(p); continue

        to_delete.append(p)

    return to_delete, protected

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="Dry-run report")
    ap.add_argument("--apply", action="store_true", help="Apply cleanup actions")
    ap.add_argument("--aggressive", action="store_true",
                    help="Allow deletion under tests/, scripts/, tools/ and __init__.py files")
    args = ap.parse_args()

    all_local = iter_local_py_files()
    reachable = build_reachable()
    unreachable = sorted(p for p in all_local - reachable)

    # Apply protection rules
    to_delete, protected = prune_unreachable(unreachable, aggressive=args.aggressive)

    print("== Repo Cleaner ==")
    print(f"Repo root: {REPO_ROOT}")
    print(f"Local .py files: {len(all_local)}")
    print(f"Reachable (by imports from entry points): {len(reachable)}")
    print(f"Unreachable (raw): {len(unreachable)}")
    if protected:
        print(f"Protected (won't delete): {len(protected)}  [use --aggressive to override]")
    print(f"Unreachable (candidates after protection): {len(to_delete)}\n")

    if to_delete:
        print("-- Unreachable python files (deletable) --")
        for p in to_delete:
            print("  ", p.relative_to(REPO_ROOT))
        print()

    if protected:
        print("-- Protected unreachable (kept) --")
        for p in protected:
            print("  ", p.relative_to(REPO_ROOT))
        print()

    # Trashy names
    trash = []
    for name in LIKELY_TRASH_NAMES:
        for p in REPO_ROOT.rglob(name):
            if any(str(p).startswith(str(ed)) for ed in EXCLUDE_DIRS):
                continue
            trash.append(p.resolve())

    if trash:
        print("-- Likely trash by name --")
        for p in sorted(trash):
            print("  ", p.relative_to(REPO_ROOT))
        print()

    # Large artifacts
    big = find_large_artifacts()
    if big:
        print("-- Large artifacts to archive (suggest move to data/archive/) --")
        for p in big:
            print("  ", p.relative_to(REPO_ROOT))
        print()

    if args.report and not args.apply:
        print("Dry run only. Nothing changed.")
        return

    if args.apply:
        # Ensure archive dir
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

        for p in to_delete:
            try:
                p.unlink()
                print("[DEL]", p.relative_to(REPO_ROOT))
            except Exception as e:
                print("[SKIP]", p, e)

        for p in trash:
            try:
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
                print("[DEL]", p.relative_to(REPO_ROOT))
            except Exception as e:
                print("[SKIP]", p, e)

        # Move artifacts
        for p in big:
            try:
                dest = ARCHIVE_DIR / p.name
                if p.resolve() != dest.resolve():
                    shutil.move(str(p), str(dest))
                    print("[MOVE]", p.relative_to(REPO_ROOT), "->", dest.relative_to(REPO_ROOT))
            except Exception as e:
                print("[SKIP-MOVE]", p, e)

        removed = delete_pycache_and_pyc()
        for p in removed:
            try:
                print("[CLEAN]", p.relative_to(REPO_ROOT))
            except Exception:
                print("[CLEAN]", p)

        print("\nApply complete. If you use git, run: git add -A && git commit -m \"repo cleanup\"")

if __name__ == "__main__":
    sys.exit(main())
