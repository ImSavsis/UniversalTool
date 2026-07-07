import requests
import yt_dlp
from backend.downloader import ffmpeg_path

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def _fmt_duration(seconds) -> str:
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return ""
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"


def _ytdlp_search(prefix: str, query: str, limit: int) -> list:
    opts = {"quiet": True, "no_warnings": True, "ignoreerrors": True, "extract_flat": "in_playlist"}
    ffmpeg = ffmpeg_path()
    if ffmpeg:
        opts["ffmpeg_location"] = ffmpeg

    results = []
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"{prefix}{limit}:{query}", download=False)
    except Exception:
        return []

    if not info:
        return []

    entries = info.get("entries") or []
    for e in entries:
        if not e:
            continue
        results.append(
            {
                "title": e.get("title") or "",
                "artist": e.get("uploader") or e.get("channel") or "",
                "cover_url": e.get("thumbnail") or (e.get("thumbnails") or [{}])[-1].get("url"),
                "duration": _fmt_duration(e.get("duration")),
                "url": e.get("url") or e.get("webpage_url") or e.get("id"),
                "source": "youtube" if prefix == "ytsearch" else "soundcloud",
            }
        )
    return results


def search_youtube(query: str, limit: int = 10) -> list:
    return _ytdlp_search("ytsearch", query, limit)


def search_soundcloud(query: str, limit: int = 10) -> list:
    return _ytdlp_search("scsearch", query, limit)


def search_apple_music(query: str, limit: int = 10) -> list:
    try:
        resp = requests.get(
            "https://itunes.apple.com/search",
            params={"term": query, "media": "music", "entity": "song", "limit": limit},
            headers={"User-Agent": _UA},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    results = []
    for row in data.get("results", []):
        cover = (row.get("artworkUrl100") or "").replace("100x100bb", "600x600bb")
        results.append(
            {
                "title": row.get("trackName") or "",
                "artist": row.get("artistName") or "",
                "cover_url": cover,
                "duration": _fmt_duration((row.get("trackTimeMillis") or 0) // 1000),
                "url": row.get("trackViewUrl") or "",
                "source": "apple_music",
            }
        )
    return results


SEARCH_FUNCS = {
    "youtube": search_youtube,
    "soundcloud": search_soundcloud,
    "apple_music": search_apple_music,
}


def search(platform: str, query: str, limit: int = 10) -> list:
    fn = SEARCH_FUNCS.get(platform)
    if not fn:
        raise ValueError(f"Unknown platform: {platform}")
    return fn(query, limit)
