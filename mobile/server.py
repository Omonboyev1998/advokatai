"""
mobile/server.py — ADVOKAT AI Android Mobil Prototiplash Serveri.

Bu server:
1. 'mobile/index.html' mobil ilovasini taqdim etadi (http://localhost:8080 va http://<WIFI_IP>:8080).
2. Har qanday Android smartfonida brauzer orqali ochilganda to'liq mobil ilova (PWA) sifatida ishlaydi.
3. Chat, Da'vo generatsiyasi, shartnoma auditi va litsenziya API larini taqdim etadi.
"""

from __future__ import annotations
import http.server
import json
import socket
import socketserver
import sys
import urllib.parse
from pathlib import Path

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core import licensing
from core import court_templates

PORT = 8080
MOBILE_DIR = Path(__file__).resolve().parent
INDEX_HTML = MOBILE_DIR / "index.html"
MANIFEST_JSON = MOBILE_DIR / "manifest.json"
FACE_PNG = ROOT / "face.png"


def get_local_ip() -> str:
    """Kompyuterning mahalliy WiFi / Tarmoq IP manzilini topish."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class AdvokatMobileHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path in ("/", "/index.html", "/mobile"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(INDEX_HTML.read_bytes())
            return

        if parsed.path == "/manifest.json":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(MANIFEST_JSON.read_bytes())
            return

        if parsed.path in ("/face.png", "/icon.png", "/avatar.png"):
            if FACE_PNG.exists():
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                self.wfile.write(FACE_PNG.read_bytes())
                return

        if parsed.path == "/api/status":
            info = licensing.get_current_license()
            self._send_json(info)
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

        if parsed.path == "/api/chat":
            prompt = data.get("prompt", "")
            reply = self._handle_legal_chat(prompt)
            self._send_json({"reply": reply})
            return

        if parsed.path == "/api/draft":
            doc_type = data.get("type", "qarz")
            plaintiff = data.get("plaintiff", "Da'vogar")
            defendant = data.get("defendant", "Javobgar")
            amount = data.get("amount", "10000000")
            text = self._handle_draft(doc_type, plaintiff, defendant, amount)
            self._send_json({"text": text})
            return

        self.send_response(404)
        self.end_headers()

    def _send_json(self, payload: dict):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def _handle_legal_chat(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "da'vo" in prompt_lower or "ariza" in prompt_lower:
            return "Da'vo arizasini tayyorlash uchun [Da'vo] bo'limiga o'ting. Sud toifasi va tomonlar ma'lumotlarini kiritishingiz bilanoq my.sud.uz standarti bo'yicha tayyor qilib beraman."
        if "shartnoma" in prompt_lower or "audit" in prompt_lower:
            return "Shartnomalarni tekshirish uchun [Audit] bo'limiga shartnoma matnini joylang. Men bir tomonlama jarimalar, noaniq muddatlar va huquqiy xatarlarni aniqlab beraman."
        if "boj" in prompt_lower or "hisob" in prompt_lower:
            return "Davlat boji O'zbekiston Respublikasi 'Davlat boji to'g'risida'gi Qonuniga asosan: fuqarolik sudlarida mulkiy da'volar uchun da'vo bahosining 4% miqdorida (kamida 1 BHM = 375 000 so'm) belgilanadi. Aniq hisoblash uchun [Hisob] bo'limidan foydalaning."
        return (
            f"Hurmatli foydalanuvchi! Savolingiz: '{prompt}'.\n"
            "O'zbekiston Respublikasi amaldagi qonunchiligi asosida sizga yuridik yordam berishga tayyorman. "
            "Iltimos, ish holatlarini batafsilroq yozing yoki kerakli bo'limni tanlang."
        )

    def _handle_draft(self, doc_type: str, p: str, d: str, amount: str) -> str:
        try:
            amt_num = int(amount)
            amt_str = f"{amt_num:,}".replace(",", " ")
        except Exception:
            amt_str = amount

        titles = {
            "qarz": "Qarz summasini undirish to'g'risida",
            "nikoh": "Nikohni bekor qilish to'g'risida",
            "aliment": "Voyaga yetmagan bolalar ta'minoti uchun aliment undirish to'g'risida",
            "zarar": "Yetkazilgan moddiy zararni undirish to'g'risida",
            "mehnat": "Ishga tiklash va majburiy progul uchun ish haqi undirish to'g'risida"
        }
        title = titles.get(doc_type, "Da'vo arizasi")

        return f"""FUQAROLIK ISHLARI BO'YICHA SUDGA

Da'vogar: {p}
Manzili: O'zbekiston Respublikasi, Toshkent sh.
Telefon: +998 (90) 123-45-67

Javobgar: {d}
Manzili: O'zbekiston Respublikasi
Da'vo bahosi: {amt_str} so'm
Davlat boji: {int(int(amount or 0) * 0.04):,} so'm

DA'VO ARIZASI
({title})

O'zbekiston Respublikasi Fuqarolik Kodeksining tegishli moddalari hamda Fuqarolik protsessual kodeksining 188, 189, 191-moddalariga asosan:

MENI ARZIM SHUNDAN IBORATKI:
Javobgar {d} o'z majburiyatlarini bajarmasdan, shartnoma shartlarini buzib kelmoqda. Natijada da'vogar {p} ga {amt_str} so'm miqdorida zarar yetkazildi. 

Yuqoridagilarga ko'ra, SUDDAN SO'RAYMAN:
1. Javobgar {d} dan da'vogar {p} foydasiga {amt_str} so'm asosiy qarz summasini undirishni;
2. Da'vogar tomonidan to'langan davlat boji va pochta xarajatlarini javobgar hisobidan undirishni.

Ilova:
1. Shaxsni tasdiqlovchi hujjat nusxasi.
2. Da'vo asoslarini tasdiqlovchi dalillar (shartnoma, dalolatnoma, to'lov topshiriqnomalari).
3. Davlat boji to'langanligi to'g'risida kvitansiya.
4. Javobgarga da'vo arizasi nusxasi yuborilganligi to'g'risida pochta kvitansiyasi.

Sana: 20.10.2026 y.
Da'vogar: {p} _______________ (imzo)"""


def run_mobile_server(port: int = PORT):
    local_ip = get_local_ip()
    server_address = ("0.0.0.0", port)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(server_address, AdvokatMobileHandler) as httpd:
        print("\n" + "=" * 65)
        print("📱 ADVOKAT AI — ANDROID MOBIL PROTOTIP ISHGA TUSHDI")
        print("=" * 65)
        print(f"Kompyuterda ko'rish  : http://localhost:{port}")
        print(f"Android telefonda    : http://{local_ip}:{port}")
        print("-" * 65)
        print("💡 QO'LLANMA:")
        print("1. Android telefoningiz va kompyuteringiz bir xil Wi-Fi tarmog'ida bo'lsin.")
        print(f"2. Telefoningizdagi Chrome brauzerida http://{local_ip}:{port} manzilini oching.")
        print("3. Brauzer menyusidan 'Bosh ekranga qo'shish' (Add to Home screen) ni tanlang.")
        print("   Ilova smartfoningizga xuddi haqiqiy APK ilovadek o'rnatiladi!")
        print("=" * 65 + "\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer to'xtatildi.")


if __name__ == "__main__":
    run_mobile_server()
