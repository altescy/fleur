from __future__ import annotations

import argparse
import errno
import logging
import os
import queue
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from ._loader import load_component
from .base import Subcommand

logger = logging.getLogger(__name__)

# --- Hot reload state (shared between threads) ---

_html_lock = threading.Lock()
_current_html: str = ""
_sse_clients: list[queue.SimpleQueue[str | None]] = []
_sse_lock = threading.Lock()


def _set_html(html: str) -> None:
    global _current_html
    with _html_lock:
        _current_html = html


def _get_html() -> str:
    with _html_lock:
        return _current_html


def _broadcast_reload() -> None:
    with _sse_lock:
        dead: list[queue.SimpleQueue[str | None]] = []
        for q in _sse_clients:
            try:
                q.put_nowait("reload")
            except Exception:
                dead.append(q)
        for q in dead:
            _sse_clients.remove(q)


# --- SSE injection snippet ---

_SSE_SCRIPT = """
<script>
(function() {
  var es = new EventSource('/__fleur_dev_reload__');
  es.addEventListener('reload', function() { location.reload(); });
  es.onerror = function() { setTimeout(function() { location.reload(); }, 1000); };
})();
</script>
"""


def _inject_sse(html: str) -> str:
    """Inject SSE reload snippet just before </body>."""
    lower = html.lower()
    idx = lower.rfind("</body>")
    if idx != -1:
        return html[:idx] + _SSE_SCRIPT + html[idx:]
    return html + _SSE_SCRIPT


# --- HTTP server + handler ---

_IGNORED_CONN_ERRORS = (BrokenPipeError, ConnectionResetError, ConnectionAbortedError)
_IGNORED_ERRNOS = {errno.ECONNRESET, errno.ECONNABORTED, errno.EPIPE}


class _DevServer(ThreadingHTTPServer):
    def handle_error(self, request: Any, client_address: Any) -> None:
        exc = sys.exc_info()[1]
        if isinstance(exc, _IGNORED_CONN_ERRORS):
            return
        if isinstance(exc, OSError) and exc.errno in _IGNORED_ERRNOS:
            return
        super().handle_error(request, client_address)


class _DevHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        logger.debug(format, *args)

    def do_GET(self) -> None:
        if self.path == "/__fleur_dev_reload__":
            self._handle_sse()
        else:
            self._handle_page()

    def _handle_page(self) -> None:
        html = _inject_sse(_get_html()).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)

    def _handle_sse(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        q: queue.SimpleQueue[str | None] = queue.SimpleQueue()
        with _sse_lock:
            _sse_clients.append(q)

        try:
            while True:
                try:
                    event = q.get(timeout=15)
                    if event is None:
                        break
                    data = f"event: {event}\ndata: \n\n"
                    self.wfile.write(data.encode("utf-8"))
                    self.wfile.flush()
                except queue.Empty:
                    # Send a keep-alive comment
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
        except Exception:
            pass
        finally:
            with _sse_lock:
                try:
                    _sse_clients.remove(q)
                except ValueError:
                    pass


def _build_html(target: str, page: Any, theme: Any, template: Any) -> str:
    from fleur import bloom

    component = load_component(target)
    return bloom(component, page=page, theme=theme, template=template)


# --- File watcher ---


def _watch_files(target: str, watch_dir: Path, poll_interval: float, page: Any, theme: Any, template: Any) -> None:
    """Poll for file changes and rebuild/broadcast on change."""

    def _snapshot(directory: Path) -> dict[Path, float]:
        result: dict[Path, float] = {}
        for root, _, files in os.walk(directory):
            for fname in files:
                if fname.endswith(".py"):
                    fp = Path(root) / fname
                    try:
                        result[fp] = fp.stat().st_mtime
                    except OSError:
                        pass
        return result

    prev = _snapshot(watch_dir)

    while True:
        time.sleep(poll_interval)
        current = _snapshot(watch_dir)
        changed = current != prev
        prev = current
        if changed:
            logger.info("Change detected, rebuilding...")
            print("\r  Detected change, rebuilding...", flush=True)
            try:
                html = _build_html(target, page, theme, template)
                _set_html(html)
                _broadcast_reload()
                print("  Rebuilt successfully.", flush=True)
            except Exception as exc:
                print(f"  Build error: {exc}", flush=True)
                logger.exception("Build error")


# --- Subcommand ---


@Subcommand.register("dev")
class DevCommand(Subcommand):
    """Start the development server with hot reload."""

    def setup(self) -> None:
        self.parser.add_argument(
            "target",
            help="Component to serve, in 'module:attribute' format (e.g. 'myapp:App' or 'path/to/app.py:App').",
        )
        self.parser.add_argument(
            "--host",
            default="127.0.0.1",
            help="Host to bind to (default: 127.0.0.1).",
        )
        self.parser.add_argument(
            "--port",
            type=int,
            default=8000,
            help="Port to listen on (default: 8000).",
        )
        self.parser.add_argument(
            "--reload-dir",
            default=None,
            metavar="DIR",
            help="Directory to watch for changes (default: current working directory).",
        )
        self.parser.add_argument(
            "--poll-interval",
            type=float,
            default=0.5,
            metavar="SECONDS",
            help="File poll interval in seconds (default: 0.5).",
        )

    def run(self, args: argparse.Namespace) -> None:
        target: str = args.target
        host: str = args.host
        port: int = args.port
        poll_interval: float = args.poll_interval
        watch_dir = Path(args.reload_dir) if args.reload_dir else Path.cwd()

        # Add watch_dir to sys.path so local modules can be imported
        watch_dir_str = str(watch_dir)
        if watch_dir_str not in sys.path:
            sys.path.insert(0, watch_dir_str)

        print(f"  Building {target}...")
        try:
            html = _build_html(target, None, None, None)
        except Exception as exc:
            print(f"  Build failed: {exc}")
            raise SystemExit(1) from exc

        _set_html(html)

        # Start file watcher thread
        watcher = threading.Thread(
            target=_watch_files,
            args=(target, watch_dir, poll_interval, None, None, None),
            daemon=True,
            name="fleur-watcher",
        )
        watcher.start()

        # Start HTTP server
        server = _DevServer((host, port), _DevHandler)
        print(f"  Serving at http://{host}:{port}")
        print("  Watching for changes... (Ctrl+C to stop)")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n  Stopping dev server.")
        finally:
            server.server_close()
