"""GamePilot bootstrap helper — cross-platform Make recipes in pure Python.

The Makefile delegates here so that the same commands work identically on
Windows (cmd.exe / PowerShell), macOS, and Linux. No shell-isms, no
``command -v``, no backtick-continuations, no ``if [ -d ... ]`` — all of
which break under ``cmd.exe``.

Every subcommand prints what it's about to do, exits with a non-zero
status on failure, and is safe to re-run (idempotent).

Usage::

    python scripts/bootstrap.py install-uv
    python scripts/bootstrap.py ensure-venv [--python 3.11] [--dir .venv]
    python scripts/bootstrap.py ensure-deps [--dev]
    python scripts/bootstrap.py clean
    python scripts/bootstrap.py stop
    python scripts/bootstrap.py open-frontend
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VENV = REPO_ROOT / ".venv"
DEFAULT_PYTHON = "3.11"
IS_WINDOWS = os.name == "nt"


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def info(msg: str) -> None:
    print(f"[bootstrap] {msg}", flush=True)


def warn(msg: str) -> None:
    print(f"[bootstrap] WARN  {msg}", flush=True)


def fail(msg: str, code: int = 1) -> "NoReturn":  # type: ignore[name-defined]
    print(f"[bootstrap] ERROR {msg}", file=sys.stderr, flush=True)
    sys.exit(code)


def which(cmd: str) -> Optional[str]:
    """Cross-platform PATH lookup (``shutil.which`` handles ``.exe``/``.cmd``)."""
    path = shutil.which(cmd)
    if path:
        return path
    if IS_WINDOWS:
        # Common explicit fallbacks for tools installed by the official
        # uv installer that aren't on PATH yet (fresh install, no relog).
        for candidate in (
            Path(os.environ.get("USERPROFILE", "")) / ".local" / "bin" / f"{cmd}.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "uv" / f"{cmd}.exe",
            Path(os.environ.get("CARGO_HOME", "")) / "bin" / f"{cmd}.exe",
        ):
            if candidate.is_file():
                return str(candidate)
    else:
        for candidate in (
            Path.home() / ".local" / "bin" / cmd,
            Path.home() / ".cargo" / "bin" / cmd,
        ):
            if candidate.is_file():
                return str(candidate)
    return None


def run(cmd: Sequence[str], *, check: bool = True, cwd: Optional[Path] = None) -> int:
    """Run a subprocess, echoing the command. Returns the exit code."""
    pretty = " ".join(str(c) for c in cmd)
    info(f"$ {pretty}")
    proc = subprocess.run(list(cmd), cwd=str(cwd) if cwd else None, check=False)
    if check and proc.returncode != 0:
        fail(f"command failed (exit {proc.returncode}): {pretty}", proc.returncode)
    return proc.returncode


# ---------------------------------------------------------------------------
# install-uv
# ---------------------------------------------------------------------------

def cmd_install_uv(_args: argparse.Namespace) -> None:
    if which("uv"):
        info("uv already installed (skipping).")
        return

    info("Installing uv package manager…")
    if IS_WINDOWS:
        # Official PowerShell installer. ``-NoProfile`` keeps it deterministic.
        ps_cmd = (
            "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force; "
            "irm https://astral.sh/uv/install.ps1 | iex"
        )
        run(["powershell", "-NoProfile", "-Command", ps_cmd])
    else:
        installer = "/tmp/uv-install.sh"
        try:
            info("Downloading https://astral.sh/uv/install.sh")
            with urllib.request.urlopen(
                "https://astral.sh/uv/install.sh", timeout=30
            ) as resp:
                Path(installer).write_bytes(resp.read())
            os.chmod(installer, 0o755)
            run(["sh", installer])
        finally:
            try:
                os.remove(installer)
            except OSError:
                pass

    if not which("uv"):
        fail(
            "uv installed but not on PATH. Open a new shell, or add "
            "%USERPROFILE%\\.local\\bin (Windows) / ~/.local/bin (Unix) to PATH."
        )
    info("uv installed.")


# ---------------------------------------------------------------------------
# ensure-venv
# ---------------------------------------------------------------------------

def _venv_python_path(venv: Path) -> Path:
    """Return the path to the python executable inside the venv."""
    if IS_WINDOWS:
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def _force_remove_dir(path: Path) -> None:
    """``shutil.rmtree`` that handles Windows symlink + read-only quirks.

    The pip / uv venv layout on Windows includes ``lib64`` as a junction
    (created by uv). On some volumes Windows can't delete the junction
    via the canonical path uv uses, which surfaces as
    ``Access is denied (os error 5)``. We fall back to clearing the
    read-only bit and to ``rmdir /s /q`` (cmd) as a last resort so a
    half-broken venv never blocks ``make install``.
    """
    if not path.exists():
        return

    def _on_error(func, p, _exc):  # noqa: ANN001
        try:
            os.chmod(p, 0o700)
            func(p)
        except OSError:
            pass

    try:
        shutil.rmtree(path, onerror=_on_error)
    except OSError:
        pass

    if path.exists() and IS_WINDOWS:
        # cmd's ``rd /s /q`` knows how to delete junctions safely.
        subprocess.call(["cmd", "/c", "rd", "/s", "/q", str(path)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def cmd_ensure_venv(args: argparse.Namespace) -> None:
    venv = Path(args.dir).resolve()
    py = args.python

    if venv.is_dir() and _venv_python_path(venv).is_file():
        info(f"{venv} already exists (skipping venv creation).")
        return

    if not which("uv"):
        cmd_install_uv(args)

    # If the directory exists but the interpreter is missing, the venv is
    # half-built (e.g. previous run hit a Windows symlink-permission error).
    # Remove it ourselves so ``uv venv`` doesn't prompt for confirmation
    # and so we sidestep its own removal logic, which fails on
    # ``lib64`` / stale junctions on Windows.
    if venv.exists():
        warn(f"Existing {venv} is incomplete — removing before recreate.")
        _force_remove_dir(venv)
        if venv.exists():
            fail(
                f"Could not delete {venv}. Close any IDE/terminal that has "
                f"the venv activated, then re-run."
            )

    info(f"Creating virtual environment in {venv} using Python {py}…")
    run(["uv", "venv", "--python", py, str(venv)])
    if not _venv_python_path(venv).is_file():
        fail(f"venv creation reported success but no interpreter at {_venv_python_path(venv)}")
    info("Virtual environment created.")


# ---------------------------------------------------------------------------
# ensure-deps
# ---------------------------------------------------------------------------

def cmd_ensure_deps(args: argparse.Namespace) -> None:
    cmd_ensure_venv(args)

    pyproject = REPO_ROOT / "pyproject.toml"
    requirements = REPO_ROOT / "requirements.txt"
    requirements_dev = REPO_ROOT / "requirements-dev.txt"

    if pyproject.is_file():
        extras: List[str] = []
        if args.dev:
            extras.append("dev")
        if getattr(args, "prod", False):
            extras.append("prod")

        if extras:
            cmd = ["uv", "sync"]
            for e in extras:
                cmd.extend(["--extra", e])
            info(f"Ensuring dependencies via uv sync ({', '.join('--extra ' + e for e in extras)})…")
            run(cmd)
        else:
            info("Ensuring production dependencies via uv sync --no-dev…")
            run(["uv", "sync", "--no-dev"])
        return

    if requirements.is_file():
        info("Ensuring dependencies via requirements.txt (no pyproject.toml)…")
        run(["uv", "pip", "install", "--upgrade", "pip"])
        run(["uv", "pip", "install", "-r", str(requirements)])
        if args.dev and requirements_dev.is_file():
            run(["uv", "pip", "install", "-r", str(requirements_dev)])
        return

    fail("No pyproject.toml or requirements.txt found.")


# ---------------------------------------------------------------------------
# clean
# ---------------------------------------------------------------------------

_CLEAN_DIRS = ("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "htmlcov")
_CLEAN_DIR_GLOBS = ("*.egg-info",)
_CLEAN_FILE_GLOBS = ("*.pyc", "*.pyo")
_CLEAN_FILES = (".coverage",)


def _rm_tree(path: Path) -> None:
    if not path.exists():
        return
    info(f"  rm -rf {path.relative_to(REPO_ROOT)}")
    shutil.rmtree(path, ignore_errors=True)


def cmd_clean(_args: argparse.Namespace) -> None:
    info("Cleaning temporary files…")
    skip_dirs = {".venv", ".git", "node_modules", "logs", "data"}

    for root, dirs, files in os.walk(REPO_ROOT, topdown=True):
        # Don't descend into heavyweight dirs we never want to scan.
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        rp = Path(root)

        # Directories named like __pycache__ etc.
        for d in list(dirs):
            if d in _CLEAN_DIRS or any(Path(d).match(g) for g in _CLEAN_DIR_GLOBS):
                _rm_tree(rp / d)
                dirs.remove(d)

        for f in files:
            fp = rp / f
            if any(fp.match(g) for g in _CLEAN_FILE_GLOBS):
                try:
                    fp.unlink()
                except OSError:
                    pass

    for f in _CLEAN_FILES:
        target = REPO_ROOT / f
        if target.exists():
            try:
                target.unlink()
            except OSError:
                pass
    info("Cleanup complete!")


# ---------------------------------------------------------------------------
# start / stop  — manage the GamePilot dev server (cross-platform)
# ---------------------------------------------------------------------------

PIDFILE_DEV       = REPO_ROOT / ".gamepilot.pid"
PIDFILE_GUNICORN  = REPO_ROOT / ".gunicorn.pid"
LOGFILE_DEV       = REPO_ROOT / "logs" / "gamepilot-server.log"
DEFAULT_HOST      = "127.0.0.1"
DEFAULT_PORT      = 8000

_STOP_PATTERNS = (
    "gamepilot.app.api.server",
    "uvicorn gamepilot",
    "uvicorn.workers.UvicornWorker",
    "gunicorn",
)


def _kill_pid(pid: int) -> bool:
    """Best-effort kill of a single PID. Returns True if the kill was issued."""
    try:
        if IS_WINDOWS:
            res = subprocess.call(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return res == 0
        os.kill(pid, 15)
        return True
    except (ProcessLookupError, PermissionError, OSError):
        return False


def _kill_pidfile(path: Path, label: str) -> None:
    if not path.is_file():
        return
    try:
        pid = int(path.read_text().strip())
    except ValueError:
        path.unlink(missing_ok=True)  # type: ignore[arg-type]
        return
    info(f"  killing {label} pid {pid}")
    _kill_pid(pid)
    try:
        path.unlink()
    except OSError:
        pass


def _probe_host(host: str) -> str:
    """A bind host like 0.0.0.0 / :: is not a valid client target on Windows
    and is unreliable everywhere else. Translate it to the loopback the
    OS will actually accept when probing locally."""
    if host in ("0.0.0.0", "", "::", "[::]"):
        return "127.0.0.1"
    return host


def _is_server_up(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: float = 1.0) -> bool:
    target = _probe_host(host)
    try:
        with urllib.request.urlopen(
            f"http://{target}:{port}/health", timeout=timeout
        ) as resp:
            return resp.status == 200
    except Exception:
        return False


def _wait_for_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    deadline_seconds: float = 30.0,
) -> bool:
    import time

    deadline = time.time() + deadline_seconds
    while time.time() < deadline:
        if _is_server_up(host, port, timeout=1.0):
            return True
        time.sleep(0.4)
    return False


def cmd_stop(_args: argparse.Namespace) -> None:
    info("Stopping GamePilot services…")

    _kill_pidfile(PIDFILE_DEV, "gamepilot dev server")
    _kill_pidfile(PIDFILE_GUNICORN, "gunicorn")

    # Pattern-based sweep as a safety net — catches workers, orphan reloads,
    # or anything started outside the pidfile flow.
    if IS_WINDOWS:
        ps = (
            "$pat = @(" + ", ".join(f"'{p}'" for p in _STOP_PATTERNS) + ");"
            "Get-CimInstance Win32_Process | Where-Object {"
            "  $cl = $_.CommandLine;"
            "  if ($cl) { $pat | Where-Object { $cl -like \"*$_*\" } }"
            "} | ForEach-Object { Write-Host \"  killing pid $($_.ProcessId) ($($_.Name))\";"
            "Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
        )
        subprocess.call(
            ["powershell", "-NoProfile", "-Command", ps],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        for pat in _STOP_PATTERNS:
            subprocess.call(
                ["pkill", "-f", pat],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    info("All services stopped.")


def cmd_start(args: argparse.Namespace) -> None:
    """One-shot: spawn the FastAPI server in the background and open the UI."""
    import time
    import webbrowser

    host = args.host
    port = args.port
    url_app = f"http://{'localhost' if host in ('0.0.0.0', '127.0.0.1') else host}:{port}/app"
    url_landing = url_app.rsplit("/app", 1)[0] + "/"

    # Already running? Just open the browser and exit.
    if _is_server_up(host, port, timeout=1.0):
        info(f"GamePilot already running on {url_landing} — opening UI.")
        if not args.no_browser:
            webbrowser.open(url_app)
        return

    # Stale pidfile? Try to clean it up before spawning.
    if PIDFILE_DEV.is_file():
        warn("Stale .gamepilot.pid found — running stop sweep first.")
        cmd_stop(args)

    # Spawn detached server.
    LOGFILE_DEV.parent.mkdir(parents=True, exist_ok=True)
    info(f"Starting GamePilot server on {url_landing} (logs → {LOGFILE_DEV})…")

    cmd = [
        "uv", "run", "uvicorn", args.app,
        "--host", host, "--port", str(port),
        "--log-level", "info",
    ]
    if args.workers and args.workers > 1:
        cmd += ["--workers", str(args.workers)]

    log_fh = open(LOGFILE_DEV, "ab", buffering=0)
    popen_kwargs: dict = {
        "cwd": str(REPO_ROOT),
        "stdout": log_fh,
        "stderr": log_fh,
        "stdin": subprocess.DEVNULL,
        # Pass the resolved frontend dir explicitly so the FastAPI server
        # finds it regardless of editable / wheel install layout.
        "env": {**os.environ, "GAMEPILOT_FRONTEND_DIR": str(REPO_ROOT / "frontend")},
    }

    if IS_WINDOWS:
        # CREATE_NO_WINDOW (0x08000000) — don't pop a console for the
        #   spawned uv/uvicorn process. Without this, Windows flashes a
        #   stray cmd window that confuses non-technical users.
        # CREATE_NEW_PROCESS_GROUP (0x00000200) — Ctrl-C in this script
        #   shouldn't propagate to the server.
        # We deliberately avoid DETACHED_PROCESS: it conflicts with the
        # behaviour of cmd-script wrappers (uv ships as uv.exe so this
        # is mostly fine, but combining DETACHED with CREATE_NO_WINDOW
        # has surprising effects depending on the binary).
        CREATE_NO_WINDOW = 0x08000000
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        popen_kwargs["creationflags"] = CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
        popen_kwargs["close_fds"] = True
    else:
        popen_kwargs["start_new_session"] = True

    proc = subprocess.Popen(cmd, **popen_kwargs)
    PIDFILE_DEV.write_text(str(proc.pid))
    info(f"  spawned pid {proc.pid}")

    # Wait until /health responds, or surface log tail on failure.
    if not _wait_for_server(host, port, deadline_seconds=args.wait):
        warn(
            f"Server did not respond on http://{host}:{port}/health within "
            f"{args.wait:.0f}s. Showing the last 40 log lines:"
        )
        try:
            print()
            for line in LOGFILE_DEV.read_text(errors="replace").splitlines()[-40:]:
                print("  | " + line)
            print()
        except OSError:
            pass
        warn("Use `make stop` to clean up, then re-run `make start`.")
        sys.exit(1)

    info("GamePilot is up.")
    print()
    print(f"  Landing  →  {url_landing}")
    print(f"  App UI   →  {url_app}")
    print(f"  News tab →  {url_app}#news")
    print()
    print(f"  Logs     →  {LOGFILE_DEV}")
    print(f"  Stop     →  make stop")
    print()

    if not args.no_browser:
        # Tiny delay so the browser doesn't beat the first-paint route.
        time.sleep(0.3)
        try:
            webbrowser.open(url_app)
        except Exception as exc:  # noqa: BLE001
            warn(f"Could not auto-open browser: {exc}. Open {url_app} manually.")


# ---------------------------------------------------------------------------
# open-frontend  — best-effort browser launch
# ---------------------------------------------------------------------------

def cmd_open_frontend(_args: argparse.Namespace) -> None:
    target = REPO_ROOT / "frontend" / "index.html"
    if not target.is_file():
        fail(f"Not found: {target}")

    info(f"Opening {target} (best-effort)…")
    try:
        if IS_WINDOWS:
            os.startfile(str(target))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(target)])
        else:
            subprocess.Popen(["xdg-open", str(target)])
    except Exception as exc:  # noqa: BLE001
        warn(f"Could not auto-open: {exc}. Open it manually: {target}")


# ---------------------------------------------------------------------------
# help  — printed banner for `make help`. Lives here so the Makefile recipe
# doesn't have to deal with cross-shell echo quirks (cmd's ``@echo.`` vs
# sh's ``echo``).
# ---------------------------------------------------------------------------

_HELP_LINES = (
    "GamePilot — Available Commands",
    "",
    "  Just three things to remember",
    "    make install            One-time setup: installs uv, .venv, and all deps",
    "    make start              Starts the server and opens the UI in your browser",
    "    make stop               Stops everything",
    "",
    "  Setup (advanced)",
    "    make install-dev        Install Python dependencies + dev tools",
    "    make setup              Same as install, plus creates project folders",
    "    make health-check       Run health check (does not reinstall)",
    "    make quickstart         Setup + sample data, then prints next steps",
    "",
    "  Run (advanced)",
    "    make run-api            Run server in foreground with --reload (dev mode)",
    "    make run-frontend       Open frontend/index.html as a local file",
    "    make production         Run API in production mode",
    "                              Linux/macOS: gunicorn + uvicorn workers",
    "                              Windows:     uvicorn --workers N",
    "    make production-stop    Stop production server",
    "    make production-logs    Tail production error log",
    "",
    "  Dev",
    "    make test               Run all tests",
    "    make test-coverage      Run tests with coverage report",
    "    make lint               Run code linters (flake8 / pylint)",
    "    make format             Format code with black",
    "",
    "  Data + training (legacy)",
    "    make data               Generate sample data",
    "    make train-nn           Train Neural Network model",
    "    make train-transformer  Train Transformer model",
    "    make train-all          Train both models",
    "",
    "  Cleanup",
    "    make clean              Clean temporary files",
    "    make clean-all          Clean everything (including models and data)",
    "",
)


def cmd_help(_args: argparse.Namespace) -> None:
    for line in _HELP_LINES:
        print(line)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bootstrap", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("install-uv", help="Install the uv package manager if missing.")

    p_venv = sub.add_parser("ensure-venv", help="Create .venv if missing.")
    p_venv.add_argument("--python", default=DEFAULT_PYTHON)
    p_venv.add_argument("--dir", default=str(DEFAULT_VENV))

    p_deps = sub.add_parser("ensure-deps", help="Install production (or dev) deps.")
    p_deps.add_argument("--python", default=DEFAULT_PYTHON)
    p_deps.add_argument("--dir", default=str(DEFAULT_VENV))
    p_deps.add_argument("--dev", action="store_true")
    p_deps.add_argument(
        "--prod",
        action="store_true",
        help="Also install the [prod] extra (gunicorn — POSIX only).",
    )

    sub.add_parser("clean", help="Remove __pycache__/.pytest_cache/etc.")
    sub.add_parser("stop", help="Stop running GamePilot services.")
    sub.add_parser("open-frontend", help="Best-effort open frontend/index.html.")
    sub.add_parser("help", help="Print the Make help banner (cross-platform).")

    p_start = sub.add_parser(
        "start",
        help="Spawn the FastAPI server in the background and open the UI.",
    )
    p_start.add_argument("--host", default=DEFAULT_HOST)
    p_start.add_argument("--port", type=int, default=DEFAULT_PORT)
    p_start.add_argument(
        "--app", default="gamepilot.app.api.server:app",
        help="ASGI application to serve (default: gamepilot.app.api.server:app).",
    )
    p_start.add_argument("--workers", type=int, default=1)
    p_start.add_argument("--wait", type=float, default=30.0,
                         help="Seconds to wait for the server to come up.")
    p_start.add_argument("--no-browser", action="store_true",
                         help="Don't auto-open the browser.")

    return parser


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = _build_parser().parse_args(list(argv) if argv is not None else None)
    handlers = {
        "install-uv": cmd_install_uv,
        "ensure-venv": cmd_ensure_venv,
        "ensure-deps": cmd_ensure_deps,
        "clean": cmd_clean,
        "stop": cmd_stop,
        "start": cmd_start,
        "open-frontend": cmd_open_frontend,
        "help": cmd_help,
    }
    handlers[args.cmd](args)


if __name__ == "__main__":
    main()
