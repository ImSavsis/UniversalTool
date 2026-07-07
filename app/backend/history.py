import json
import threading
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
HISTORY_FILE = PROJECT_DIR / "data" / "history.json"
MAX_ENTRIES = 200

_LOCK = threading.Lock()


def _load() -> list:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save(entries: list):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def add_history_entry(file_path: str, meta: dict, fmt: str) -> dict:
    entry = {
        "title": meta.get("title") or Path(file_path).stem,
        "artist": meta.get("artist") or "",
        "cover_url": meta.get("cover_url"),
        "format": fmt,
        "path": file_path,
        "timestamp": time.time(),
    }
    with _LOCK:
        entries = _load()
        entries.insert(0, entry)
        entries = entries[:MAX_ENTRIES]
        _save(entries)
    return entry


def get_history(limit: int = 50) -> list:
    with _LOCK:
        return _load()[:limit]


def clear_history():
    with _LOCK:
        _save([])
