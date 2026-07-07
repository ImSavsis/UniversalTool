import ast
import platform
import subprocess
import urllib.request
import zipfile
import io
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
BIN_DIR = PROJECT_DIR / "bin"

STYLUA_VERSION = "0.20.0"
STYLUA_URL = (
    f"https://github.com/JohnnyMorganz/StyLua/releases/download/v{STYLUA_VERSION}/"
    f"stylua-windows-x86_64.zip"
)


def format_python(code: str) -> dict:
    try:
        ast.parse(code)
    except SyntaxError as e:
        return {
            "ok": False,
            "error": f"SyntaxError: {e.msg}",
            "line": e.lineno,
            "formatted": code,
        }

    try:
        import black
        formatted = black.format_str(code, mode=black.Mode())
        return {"ok": True, "error": None, "line": None, "formatted": formatted}
    except Exception as e:
        return {"ok": False, "error": str(e), "line": None, "formatted": code}


def _stylua_exe() -> Path:
    return BIN_DIR / ("stylua.exe" if platform.system() == "Windows" else "stylua")


def _ensure_stylua() -> Path | None:
    exe = _stylua_exe()
    if exe.exists():
        return exe

    if platform.system() != "Windows":
        return None

    BIN_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(STYLUA_URL, timeout=30) as resp:
            data = resp.read()
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for name in zf.namelist():
                if Path(name).name.lower() == "stylua.exe":
                    exe.write_bytes(zf.read(name))
                    return exe
    except Exception:
        return None
    return None


def format_lua(code: str) -> dict:
    exe = _ensure_stylua()
    if not exe:
        return {
            "ok": False,
            "error": "stylua не удалось скачать автоматически — проверь интернет или положи stylua.exe в bin\\ вручную.",
            "line": None,
            "formatted": code,
        }

    try:
        result = subprocess.run(
            [str(exe), "-"],
            input=code,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            return {"ok": False, "error": result.stderr.strip(), "line": None, "formatted": code}
        return {"ok": True, "error": None, "line": None, "formatted": result.stdout}
    except Exception as e:
        return {"ok": False, "error": str(e), "line": None, "formatted": code}


def format_code(code: str, language: str) -> dict:
    if language == "python":
        return format_python(code)
    if language == "lua":
        return format_lua(code)
    return {"ok": False, "error": f"unsupported language: {language}", "line": None, "formatted": code}
