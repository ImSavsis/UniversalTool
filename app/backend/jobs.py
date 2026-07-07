import threading
import time
import uuid
from pathlib import Path

_JOBS: dict[str, dict] = {}
_LOCK = threading.Lock()


def create_job() -> str:
    job_id = uuid.uuid4().hex[:12]
    with _LOCK:
        _JOBS[job_id] = {
            "status": "pending",
            "progress": 0,
            "speed": "",
            "filename": "",
            "error": None,
            "result": None,
            "created": time.time(),
        }
    return job_id


def get_job(job_id: str) -> dict | None:
    with _LOCK:
        job = _JOBS.get(job_id)
        return dict(job) if job else None


def _update(job_id: str, **kwargs):
    with _LOCK:
        if job_id in _JOBS:
            _JOBS[job_id].update(kwargs)


def _progress_hook(job_id: str):
    def hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done = d.get("downloaded_bytes") or 0
            pct = int(done * 100 / total) if total else 0
            speed = d.get("_speed_str") or ""
            fname = Path(d.get("filename", "")).name
            _update(job_id, status="downloading", progress=pct, speed=speed, filename=fname)
        elif d["status"] == "finished":
            _update(job_id, status="processing", progress=100)
    return hook


def run_download_job(job_id: str, url: str, fmt: str, quality: str, output_dir: str):
    from backend.downloader import download_track
    from backend.history import add_history_entry

    _update(job_id, status="downloading")
    try:
        hook = _progress_hook(job_id)
        results = download_track(url, fmt, quality, output_dir, progress_callback=hook)

        entries = []
        for file_path, meta in results:
            entry = add_history_entry(file_path, meta, fmt)
            entries.append(entry)

        _update(job_id, status="done", progress=100, result=entries)
    except Exception as e:
        _update(job_id, status="error", error=str(e))


def start_download(url: str, fmt: str, quality: str, output_dir: str) -> str:
    job_id = create_job()
    t = threading.Thread(
        target=run_download_job,
        args=(job_id, url, fmt, quality, output_dir),
        daemon=True,
    )
    t.start()
    return job_id
