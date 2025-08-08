# scripts/clean_repo.py
import argparse, os, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Patterns we consider junk
JUNK_SUFFIXES = {".pyc", ".pyo", ".pyd", ".orig", ".rej"}
JUNK_NAMES = {".DS_Store", "Thumbs.db"}
JUNK_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".cache"}
JUNK_GLOBS = [
    "*.bak", "*.bak.py", "*.save", "*.tmp", "*~",
]

# Safety: never touch these
PROTECT_DIRS = {"data", "Team Data", ".git", ".venv", "venv", "WeatherDashboard.egg-info"}
PROTECT_FILES = {"requirements.txt", "setup.py", "build.py", "main.py", "gui.py"}

def is_protected(p: Path) -> bool:
    if p.name in PROTECT_FILES:
        return True
    for part in p.parts:
        if part in PROTECT_DIRS:
            return True
    return False

def find_junk(start: Path):
    candidates = []
    for p in start.rglob("*"):
        if is_protected(p):
            continue
        if p.is_dir() and p.name in JUNK_DIRS:
            candidates.append(p)
        elif p.is_file():
            if p.suffix in JUNK_SUFFIXES or p.name in JUNK_NAMES:
                candidates.append(p)
            else:
                for pat in JUNK_GLOBS:
                    if p.match(pat):
                        candidates.append(p)
                        break
    return candidates

def main():
    ap = argparse.ArgumentParser(description="Clean repo of junk files (dry-run by default).")
    ap.add_argument("--apply", action="store_true", help="Actually delete files/directories.")
    args = ap.parse_args()

    junk = find_junk(ROOT)
    if not junk:
        print("No junk found. ✨")
        return

    print("Will remove:")
    for p in junk:
        print("  ", p.relative_to(ROOT))

    if not args.apply:
        print("\nDry-run. Re-run with --apply to delete.")
        return

    for p in junk:
        try:
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink(missing_ok=True)
        except Exception as e:
            print(f"Failed to delete {p}: {e}")
    print("Cleanup complete. ✅")

if __name__ == "__main__":
    main()
