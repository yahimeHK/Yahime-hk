#!/usr/bin/env python3
"""
LOL 攻略站 — 本機靜態伺服器。

為什麼不用 `python -m http.server`？它的 SimpleHTTPRequestHandler 不處理
Range 請求，<video> 就無法 seek，每次拖動時間軸都會重新下載整個 20 MB 檔案。
這支會回應 byte range（206 Partial Content），也就是瀏覽器拖曳時間軸時需要
的行為。同時送出 `no-store`，改完 CSS/JS 重新整理就會生效。

用法：
    python serve.py              # http://127.0.0.1:8099
    python serve.py 3000         # http://127.0.0.1:3000
    python serve.py 3000 0.0.0.0 # 開放到區域網路（小心使用）
"""

import os
import re
import sys
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
CHUNK = 1024 * 256
RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")

# 瀏覽器 seek 時會不斷取消進行中的媒體請求。在 Windows 上這表現為
# ConnectionAbortedError 而不是 BrokenPipeError，所以三者都視為正常的
# 客戶端斷線，而不是需要記錄的錯誤。
DISCONNECTS = (BrokenPipeError, ConnectionResetError, ConnectionAbortedError)

mimetypes.add_type("video/mp4", ".mp4")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("image/webp", ".webp")


class Handler(BaseHTTPRequestHandler):
    server_version = "LOLGuideDev/1.0"

    # ---------------------------------------------------------------- helpers
    def _resolve(self):
        """把請求路徑對應到 ROOT 內的真實檔案（不可穿越目錄）。"""
        path = unquote(urlparse(self.path).path)
        if path.endswith("/"):
            path += "index.html"
        candidate = os.path.abspath(os.path.join(ROOT, path.lstrip("/")))
        if os.path.commonpath([candidate, ROOT]) != ROOT:
            return None
        return candidate if os.path.isfile(candidate) else None

    def _headers(self, status, length, ctype, extra=None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(length))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()

    # ------------------------------------------------------------------ verbs
    def do_HEAD(self):
        self.do_GET(head_only=True)

    def do_GET(self, head_only=False):
        target = self._resolve()
        if not target:
            body = b"404 Not Found\n"
            self._headers(404, len(body), "text/plain; charset=utf-8")
            if not head_only:
                self.wfile.write(body)
            return

        size = os.path.getsize(target)
        ctype = mimetypes.guess_type(target)[0] or "application/octet-stream"
        rng = RANGE_RE.fullmatch((self.headers.get("Range") or "").strip())

        if not rng:
            self._headers(200, size, ctype, {"Last-Modified": self.date_time_string(os.path.getmtime(target))})
            if head_only:
                return
            with open(target, "rb") as fh:
                while True:
                    chunk = fh.read(CHUNK)
                    if not chunk:
                        break
                    try:
                        self.wfile.write(chunk)
                    except DISCONNECTS:
                        return          # 瀏覽器取消（seek 時的正常現象）
            return

        # --- byte range -----------------------------------------------------
        start_s, end_s = rng.group(1), rng.group(2)
        if start_s == "":
            if end_s == "":
                self._headers(200, size, ctype)
                return
            start, end = max(0, size - int(end_s)), size - 1     # suffix range
        else:
            start = int(start_s)
            end = int(end_s) if end_s else size - 1

        if start >= size or start > end:
            self._headers(416, 0, ctype, {"Content-Range": "bytes */%d" % size})
            return

        end = min(end, size - 1)
        length = end - start + 1
        self._headers(206, length, ctype, {"Content-Range": "bytes %d-%d/%d" % (start, end, size)})
        if head_only:
            return
        with open(target, "rb") as fh:
            fh.seek(start)
            remaining = length
            while remaining > 0:
                chunk = fh.read(min(CHUNK, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except DISCONNECTS:
                    return
                remaining -= len(chunk)

    def handle_error(self, request, client_address):
        """客戶端正常斷線時不要印出 traceback。"""
        exc = sys.exc_info()[1]
        if isinstance(exc, DISCONNECTS):
            return
        sys.stderr.write("  ! %s: %s\n" % (client_address[0], exc))

    def log_message(self, fmt, *args):
        status = args[1] if len(args) > 1 else ""
        if str(status).startswith(("2", "3")) and "mp4" in (args[0] if args else ""):
            return                                   # 不要把影片 range 的雜訊寫進 log
        sys.stderr.write("  %s %s\n" % (self.address_string(), fmt % args))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8099
    host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
    httpd = ThreadingHTTPServer((host, port), Handler)
    url = "http://%s:%d/" % ("127.0.0.1" if host == "0.0.0.0" else host, port)
    print("Serving %s" % ROOT)
    print("  ->  %s" % url)
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
