"""
web/server.py — ADVOKAT AI Rasmiy Taqdimot Sayti, Litsenziyalash va To'lov Gateway Serveri.

Bu server:
1. 'web/landing.html' rasmiy taqdimot sahifasini brauzerda taqdim etadi (http://localhost:8057).
2. /api/license/status — joriy kompyuter apparat ID va litsenziya holatini tekshiradi.
3. /api/license/activate — yangi litsenziya kalitini faollashtiradi.
4. /api/license/pay — Click yoki Payme to'lov billing havolalarini qaytaradi.
5. /api/demo/generate — jonli demo da'vo arizasini tezkor generatsiya qiladi.
"""

from __future__ import annotations
import http.server
import socketserver
import json
import urllib.parse
import webbrowser
from pathlib import Path
from core import licensing
from core import court_templates

PORT = 8057
WEB_DIR = Path(__file__).resolve().parent
LANDING_HTML = WEB_DIR / "landing.html"


class AdvokatMarketingHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        # Bosh sahifa — Landing Page
        if parsed.path in ("/", "/index.html", "/landing"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(LANDING_HTML.read_bytes())
            return

        # API: Litsenziya holati
        if parsed.path == "/api/license/status":
            info = licensing.get_current_license()
            self._send_json(info)
            return

        # API: Shablonlar ro'yxati
        if parsed.path == "/api/templates":
            items = court_templates.get_all_templates_summary()
            self._send_json({"total": len(items), "templates": items})
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        # API: Kalitni faollashtirish
        if parsed.path == "/api/license/activate":
            key = data.get("license_key", "").strip()
            res = licensing.activate_license(key)
            self._send_json(res)
            return

        # API: To'lov havolasini olish (Click / Payme)
        if parsed.path == "/api/license/pay":
            tier = data.get("tier", "solo")
            phone = data.get("phone", "")
            links = licensing.generate_payment_links(tier, phone)
            self._send_json({"success": True, "billing": links})
            return

        self.send_error(404, "API topilmadi")

    def _send_json(self, data: dict):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        # Jim rejim (konsolni to'ldirmaslik uchun)
        pass


def start_server(open_browser: bool = True):
    print("=" * 60)
    print("ADVOKAT AI RASMIY TAQDIMOT & LITSENZIYALASH SERVERI")
    print(f"Sayt manzili: http://localhost:{PORT}")
    print("=" * 60)
    
    if open_browser:
        try:
            webbrowser.open(f"http://localhost:{PORT}")
        except Exception:
            pass

    with socketserver.TCPServer(("", PORT), AdvokatMarketingHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer to'xtatildi.")


if __name__ == "__main__":
    start_server(open_browser=True)
