import os
import sys
import threading
import time
import uuid
import webbrowser
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_file

sys.path.insert(0, str(Path(__file__).parent))

from backend import downloader, search as search_mod, history as history_mod
from backend import converter, metadata, scripts_format, jobs

PROJECT_DIR = Path(__file__).parent
DOWNLOADS_DIR = PROJECT_DIR / "downloads"
UPLOAD_DIR = PROJECT_DIR / "uploads"
OUTPUT_DIR = PROJECT_DIR / "outputs"

for d in (DOWNLOADS_DIR, UPLOAD_DIR, OUTPUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 * 1024


@app.route("/")
def index():
    return render_template("index.html")


# --- downloader ---

@app.route("/api/download", methods=["POST"])
def api_download():
    data = request.json or {}
    url = (data.get("url") or "").strip()
    fmt = data.get("format", "mp3")
    quality = data.get("quality", "320")

    if not url:
        return jsonify({"error": "нет ссылки"}), 400

    job_id = jobs.start_download(url, fmt, quality, str(DOWNLOADS_DIR))
    return jsonify({"job_id": job_id})


@app.route("/api/job/<job_id>")
def api_job(job_id):
    job = jobs.get_job(job_id)
    if not job:
        return jsonify({"error": "job not found"}), 404
    return jsonify(job)


@app.route("/api/search")
def api_search():
    platform = request.args.get("platform", "youtube")
    query = request.args.get("q", "").strip()
    limit = min(int(request.args.get("limit", 10)), 25)

    if not query:
        return jsonify({"error": "пустой запрос"}), 400

    try:
        results = search_mod.search(platform, query, limit)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/history")
def api_history():
    return jsonify({"history": history_mod.get_history()})


@app.route("/api/history/clear", methods=["POST"])
def api_history_clear():
    history_mod.clear_history()
    return jsonify({"ok": True})


# --- converter ---

@app.route("/api/convert/upload", methods=["POST"])
def api_convert_upload():
    if "file" not in request.files:
        return jsonify({"error": "нет файла"}), 400

    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "имя файла пустое"}), 400

    uid = uuid.uuid4().hex[:10]
    ext = Path(f.filename).suffix
    saved_name = uid + ext
    saved_path = UPLOAD_DIR / saved_name
    f.save(saved_path)

    kind = converter.detect_type(saved_path)
    targets = converter.get_targets(kind)

    return jsonify({
        "id": uid,
        "filename": f.filename,
        "saved": saved_name,
        "type": kind,
        "size": saved_path.stat().st_size,
        "targets": targets,
    })


@app.route("/api/convert/run", methods=["POST"])
def api_convert_run():
    data = request.json or {}
    uid = data.get("id", "")
    saved = data.get("saved", "")
    target = data.get("target", "")
    original = data.get("filename", "file")

    if not all([uid, saved, target]):
        return jsonify({"error": "плохие параметры"}), 400
    if target not in converter.ALL_TARGETS:
        return jsonify({"error": "недопустимый формат"}), 400

    src = UPLOAD_DIR / Path(saved).name
    if not src.exists():
        return jsonify({"error": "файл не найден"}), 404

    out_name = f"{uid}_out.{target}"
    out_path = OUTPUT_DIR / out_name

    ok, err = converter.convert(src, out_path, target)
    if not ok:
        return jsonify({"error": err}), 500

    base = Path(Path(original).stem).stem
    result_filename = f"{base}.{target}"
    return jsonify({"result": out_name, "filename": result_filename})


@app.route("/api/convert/download/<path:filename>")
def api_convert_download(filename):
    safe = Path(filename).name
    path = OUTPUT_DIR / safe
    if not path.exists():
        return "не найдено", 404
    return send_file(path, as_attachment=True)


# --- metadata ---

@app.route("/api/metadata/upload", methods=["POST"])
def api_metadata_upload():
    if "file" not in request.files:
        return jsonify({"error": "нет файла"}), 400

    f = request.files["file"]
    ext = Path(f.filename).suffix.lower()
    if ext not in metadata.SUPPORTED_EXTS:
        return jsonify({"error": f"формат {ext} не поддерживается"}), 400

    uid = uuid.uuid4().hex[:10]
    saved_name = uid + ext
    saved_path = UPLOAD_DIR / saved_name
    f.save(saved_path)

    tags = metadata.read_tags(saved_path)
    return jsonify({"id": uid, "saved": saved_name, "filename": f.filename, "tags": tags})


@app.route("/api/metadata/cover/<path:filename>")
def api_metadata_cover(filename):
    from flask import Response
    path = UPLOAD_DIR / Path(filename).name
    if not path.exists():
        return "", 404
    data = metadata._extract_cover_bytes(path)
    if not data:
        return "", 404
    return Response(data, mimetype="image/jpeg")


@app.route("/api/metadata/save", methods=["POST"])
def api_metadata_save():
    saved = request.form.get("saved", "")
    if not saved:
        return jsonify({"error": "нет файла"}), 400

    path = UPLOAD_DIR / Path(saved).name
    if not path.exists():
        return jsonify({"error": "файл не найден"}), 404

    meta = {
        "title": request.form.get("title"),
        "artist": request.form.get("artist"),
        "album": request.form.get("album"),
        "year": request.form.get("year"),
        "track_number": request.form.get("track_number"),
    }

    cover_bytes = None
    if "cover" in request.files and request.files["cover"].filename:
        cover_bytes = metadata._cover_bytes_from_upload(request.files["cover"].read())

    try:
        metadata.write_tags(path, meta, cover_bytes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"ok": True, "download": saved})


@app.route("/api/metadata/batch", methods=["POST"])
def api_metadata_batch():
    data = request.json or {}
    ids = data.get("saved_files", [])
    meta = {
        "title": None,
        "artist": data.get("artist"),
        "album": data.get("album"),
        "year": data.get("year"),
        "track_number": None,
    }
    meta = {k: v for k, v in meta.items() if v not in (None, "")}

    cover_bytes = None
    cover_url = data.get("cover_saved")
    if cover_url:
        cover_path = UPLOAD_DIR / Path(cover_url).name
        if cover_path.exists():
            cover_bytes = metadata._cover_bytes_from_upload(cover_path.read_bytes())

    updated = []
    errors = []
    for saved in ids:
        path = UPLOAD_DIR / Path(saved).name
        if not path.exists():
            errors.append(f"{saved}: файл не найден")
            continue
        try:
            metadata.write_tags(path, meta, cover_bytes)
            updated.append(saved)
        except Exception as e:
            errors.append(f"{saved}: {e}")

    return jsonify({"updated": updated, "errors": errors})


@app.route("/api/metadata/download/<path:filename>")
def api_metadata_download(filename):
    safe = Path(filename).name
    path = UPLOAD_DIR / safe
    if not path.exists():
        return "не найдено", 404
    return send_file(path, as_attachment=True)


# --- scripts ---

@app.route("/api/scripts/format", methods=["POST"])
def api_scripts_format():
    data = request.json or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    result = scripts_format.format_code(code, language)
    return jsonify(result)


def _open_browser(url: str):
    time.sleep(1.2)
    try:
        webbrowser.open(url)
    except Exception:
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    url = f"http://127.0.0.1:{port}"
    print(f"nexdex.space  —  {url}")
    threading.Thread(target=_open_browser, args=(url,), daemon=True).start()
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)
