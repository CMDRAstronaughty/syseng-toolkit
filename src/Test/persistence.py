import json
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path.cwd() / "data"
ISSUES_DIR = DATA_DIR / "issues"

EVENTS_FILE = DATA_DIR / "test_events.json"
ISSUES_FILE = ISSUES_DIR / "test_issues.json"


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ISSUES_DIR.mkdir(parents=True, exist_ok=True)


def save_events(events: Dict[str, Any]) -> Path:
    """Save test events to JSON and return the file path."""
    ensure_dirs()
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    return EVENTS_FILE


def load_events() -> Dict[str, Any]:
    """Load test events from JSON. Returns empty dict if not found."""
    if not EVENTS_FILE.exists():
        return {}
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_issues(issues: List[Dict[str, Any]]) -> Path:
    """Save created issues to JSON and return file path."""
    ensure_dirs()
    with open(ISSUES_FILE, "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)
    return ISSUES_FILE


def load_issues() -> List[Dict[str, Any]]:
    """Load issues from JSON. Returns empty list if not found."""
    if not ISSUES_FILE.exists():
        return []
    with open(ISSUES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
