import io
import requests
from pathlib import Path
from PIL import Image

from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TRCK, TDRC
from mutagen.id3 import ID3NoHeaderError
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus

SUPPORTED_EXTS = {".mp3", ".flac", ".m4a", ".mp4", ".wav", ".ogg", ".opus"}


def _sanitize(value) -> str:
    return str(value) if value is not None else ""


def _fetch_cover(url: str) -> bytes | None:
    if not url:
        return None
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        return buf.getvalue()
    except Exception:
        return None


def _cover_bytes_from_upload(data: bytes) -> bytes:
    img = Image.open(io.BytesIO(data)).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def _extract_cover_bytes(path: Path) -> bytes | None:
    ext = path.suffix.lower()
    try:
        if ext in (".mp3", ".wav"):
            tags = ID3(path)
            for tag in tags.values():
                if tag.FrameID == "APIC":
                    return tag.data
        elif ext == ".flac":
            audio = FLAC(path)
            if audio.pictures:
                return audio.pictures[0].data
        elif ext in (".m4a", ".mp4"):
            audio = MP4(path)
            covr = audio.get("covr")
            if covr:
                return bytes(covr[0])
        elif ext == ".ogg":
            audio = OggVorbis(path)
            pics = audio.get("metadata_block_picture")
            if pics:
                import base64
                pic = Picture(base64.b64decode(pics[0]))
                return pic.data
        elif ext == ".opus":
            audio = OggOpus(path)
            pics = audio.get("metadata_block_picture")
            if pics:
                import base64
                pic = Picture(base64.b64decode(pics[0]))
                return pic.data
    except Exception:
        pass
    return None


def read_tags(path: Path) -> dict:
    ext = path.suffix.lower()
    tags = {"title": "", "artist": "", "album": "", "year": "", "track_number": "", "has_cover": False}

    try:
        if ext in (".mp3", ".wav"):
            id3 = ID3(path)
            tags["title"] = str(id3.get("TIT2", ""))
            tags["artist"] = str(id3.get("TPE1", ""))
            tags["album"] = str(id3.get("TALB", ""))
            tags["year"] = str(id3.get("TDRC", ""))
            tags["track_number"] = str(id3.get("TRCK", ""))
        elif ext == ".flac":
            audio = FLAC(path)
            tags["title"] = audio.get("title", [""])[0]
            tags["artist"] = audio.get("artist", [""])[0]
            tags["album"] = audio.get("album", [""])[0]
            tags["year"] = audio.get("date", [""])[0]
            tags["track_number"] = audio.get("tracknumber", [""])[0]
        elif ext in (".m4a", ".mp4"):
            audio = MP4(path)
            tags["title"] = (audio.get("\xa9nam") or [""])[0]
            tags["artist"] = (audio.get("\xa9ART") or [""])[0]
            tags["album"] = (audio.get("\xa9alb") or [""])[0]
            tags["year"] = (audio.get("\xa9day") or [""])[0]
        elif ext == ".ogg":
            audio = OggVorbis(path)
            tags["title"] = audio.get("title", [""])[0]
            tags["artist"] = audio.get("artist", [""])[0]
            tags["album"] = audio.get("album", [""])[0]
            tags["year"] = audio.get("date", [""])[0]
        elif ext == ".opus":
            audio = OggOpus(path)
            tags["title"] = audio.get("title", [""])[0]
            tags["artist"] = audio.get("artist", [""])[0]
            tags["album"] = audio.get("album", [""])[0]
            tags["year"] = audio.get("date", [""])[0]
    except Exception:
        pass

    tags["has_cover"] = _extract_cover_bytes(path) is not None
    return tags


def _write_mp3_like(path: Path, meta: dict, cover: bytes | None):
    try:
        tags = ID3(path)
    except ID3NoHeaderError:
        tags = ID3()

    if meta.get("title") is not None:
        tags["TIT2"] = TIT2(encoding=3, text=_sanitize(meta["title"]))
    if meta.get("artist") is not None:
        tags["TPE1"] = TPE1(encoding=3, text=_sanitize(meta["artist"]))
    if meta.get("album") is not None:
        tags["TALB"] = TALB(encoding=3, text=_sanitize(meta["album"]))
    if meta.get("track_number") is not None:
        tags["TRCK"] = TRCK(encoding=3, text=_sanitize(meta["track_number"]))
    if meta.get("year") is not None:
        tags["TDRC"] = TDRC(encoding=3, text=_sanitize(meta["year"]))
    if cover:
        tags.delall("APIC")
        tags["APIC"] = APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=cover)

    tags.save(path)


def _write_flac(path: Path, meta: dict, cover: bytes | None):
    audio = FLAC(path)

    if meta.get("title") is not None:
        audio["title"] = _sanitize(meta["title"])
    if meta.get("artist") is not None:
        audio["artist"] = _sanitize(meta["artist"])
    if meta.get("album") is not None:
        audio["album"] = _sanitize(meta["album"])
    if meta.get("track_number") is not None:
        audio["tracknumber"] = _sanitize(meta["track_number"])
    if meta.get("year") is not None:
        audio["date"] = _sanitize(meta["year"])

    if cover:
        audio.clear_pictures()
        pic = Picture()
        pic.type = 3
        pic.mime = "image/jpeg"
        pic.data = cover
        audio.add_picture(pic)

    audio.save()


def _write_m4a(path: Path, meta: dict, cover: bytes | None):
    audio = MP4(path)

    if meta.get("title") is not None:
        audio["\xa9nam"] = [_sanitize(meta["title"])]
    if meta.get("artist") is not None:
        audio["\xa9ART"] = [_sanitize(meta["artist"])]
    if meta.get("album") is not None:
        audio["\xa9alb"] = [_sanitize(meta["album"])]
    if meta.get("year") is not None:
        audio["\xa9day"] = [_sanitize(meta["year"])]
    if meta.get("track_number"):
        try:
            audio["trkn"] = [(int(meta["track_number"]), 0)]
        except (TypeError, ValueError):
            pass
    if cover:
        audio["covr"] = [MP4Cover(cover, imageformat=MP4Cover.FORMAT_JPEG)]

    audio.save()


def _write_ogg_like(path: Path, meta: dict, cover: bytes | None, cls):
    audio = cls(path)

    if meta.get("title") is not None:
        audio["title"] = _sanitize(meta["title"])
    if meta.get("artist") is not None:
        audio["artist"] = _sanitize(meta["artist"])
    if meta.get("album") is not None:
        audio["album"] = _sanitize(meta["album"])
    if meta.get("year") is not None:
        audio["date"] = _sanitize(meta["year"])

    if cover:
        import base64
        pic = Picture()
        pic.type = 3
        pic.mime = "image/jpeg"
        pic.data = cover
        audio["metadata_block_picture"] = [base64.b64encode(pic.write()).decode("ascii")]

    audio.save()


def write_tags(path: Path, meta: dict, cover_bytes: bytes | None = None):
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTS:
        raise ValueError(f"Unsupported format: {ext}")

    if ext in (".mp3", ".wav"):
        _write_mp3_like(path, meta, cover_bytes)
    elif ext == ".flac":
        _write_flac(path, meta, cover_bytes)
    elif ext in (".m4a", ".mp4"):
        _write_m4a(path, meta, cover_bytes)
    elif ext == ".ogg":
        _write_ogg_like(path, meta, cover_bytes, OggVorbis)
    elif ext == ".opus":
        _write_ogg_like(path, meta, cover_bytes, OggOpus)


def embed_cover_and_metadata(file_path: str, meta: dict):
    """Used by the downloader right after a track finishes downloading."""
    path = Path(file_path)
    if not path.exists():
        return

    cover_data = _fetch_cover(meta.get("cover_url"))
    try:
        write_tags(
            path,
            {
                "title": meta.get("title"),
                "artist": meta.get("artist"),
                "album": meta.get("album"),
                "track_number": meta.get("track_number"),
                "year": meta.get("year"),
            },
            cover_data,
        )
    except Exception:
        pass
