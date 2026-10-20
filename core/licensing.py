"""
core/licensing.py — ADVOKAT AI (Mark 57) Kriptografik Litsenziyalash va To'lov Moduli.

Xususiyatlari:
1. Mashina apparat identifikatori (Hardware ID / Machine Fingerprint) generatsiyasi.
2. HMAC-SHA256 imzoli Litsenziya Kalitlarini (License Keys) yaratish va tekshirish.
3. Tarif rejalari: TRIAL (14 kun bepul), SOLO ADVOKAT, ADVOKATLIK BYUROSI, ENTERPRISE.
4. Click & Payme to'lov billing havolalari va ma'lumotlar integratsiyasi.
5. Doimiy xavfsiz litsenziya saqlash (%APPDATA%/AdvokatAI/data/license.key yoki data/license.key).
6. Administrator / Sotuvchi uchun CLI kalit yaratish buyruqlari.
"""

from __future__ import annotations
import argparse
import hashlib
import hmac
import json
import os
import platform
import subprocess
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


def get_license_dir() -> Path:
    """Litsenziya fayli saqlanadigan xavfsiz va doimiy papkani qaytaradi."""
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).parent
        if (exe_dir / "config").is_dir() or (exe_dir / "data").is_dir():
            d = exe_dir / "data"
        else:
            appdata = os.environ.get("APPDATA")
            d = (Path(appdata) / "AdvokatAI" / "data") if appdata else (exe_dir / "data")
    else:
        d = Path(__file__).resolve().parent.parent / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_license_file() -> Path:
    return get_license_dir() / "license.key"


# Maxfiy HMAC imzo kaliti (Xavfsiz kriptografik imzo uchun)
MASTER_SECRET = os.environ.get(
    "ADVOKAT_LICENSE_SECRET",
    "ADVOKAT_AI_SECURE_HMAC_MASTER_KEY_UZ_2026_X9_K7"
).encode("utf-8")

TIERS = {
    "trial": {
        "name": "Sinov Davri (Trial)",
        "duration_days": 14,
        "price_uzs": 0,
        "badge": "SINOB (14 KUN)",
        "features": ["davo_arizasi", "contract_audit", "calculator", "crm", "docx_export"]
    },
    "solo": {
        "name": "Solo Advokat",
        "duration_days": 30,
        "price_uzs": 390000,
        "badge": "SOLO ADVOKAT",
        "features": ["davo_arizasi", "contract_audit", "calculator", "crm", "docx_export", "lexuz_search"]
    },
    "bureau": {
        "name": "Advokatlik Byurosi",
        "duration_days": 30,
        "price_uzs": 1290000,
        "badge": "BYURO",
        "features": ["davo_arizasi", "contract_audit", "calculator", "crm", "moot_court", "docx_export", "team_access", "lexuz_search"]
    },
    "enterprise": {
        "name": "Korporativ / Enterprise",
        "duration_days": 365,
        "price_uzs": 39000000,
        "badge": "ENTERPRISE",
        "features": ["all", "on_premise", "unlimited_cases", "priority_support"]
    }
}


def get_hardware_fingerprint() -> str:
    """
    Foydalanuvchi kompyuterining unikal apparat identifikatorini (Machine ID) aniqlaydi.
    Natija formati: masalan '7A9B4C2F8E1D3A5B'
    """
    elements = [
        platform.node(),
        platform.machine(),
        platform.processor(),
        str(uuid.getnode())  # MAC address
    ]
    # Windows disk serial yoki Motherboard UUID
    if platform.system() == "Windows":
        try:
            out = subprocess.check_output(
                "wmic csproduct get uuid",
                shell=True,
                stderr=subprocess.DEVNULL
            ).decode()
            parts = [p.strip() for p in out.split() if p.strip() and "UUID" not in p]
            if parts:
                elements.append(parts[0])
        except Exception:
            pass
    raw = "|".join(elements)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16].upper()


def get_formatted_hwid() -> str:
    """Chiroyli va qulay formatdagi Kompyuter ID: masalan 'UZ-ADV-7A9B-4C2F'"""
    hw = get_hardware_fingerprint()
    return f"UZ-ADV-{hw[:4]}-{hw[4:8]}-{hw[8:12]}"


def _compute_signature(short_hw: str, tier: str, ts_str: str) -> str:
    """HMAC-SHA256 orqali 10 ta belgidan iborat imzo yaratish."""
    payload = f"{short_hw.upper()}:{tier.upper()}:{ts_str}"
    return hmac.new(MASTER_SECRET, payload.encode("utf-8"), hashlib.sha256).hexdigest()[:10].upper()


def generate_license_key(hw_id: str, tier: str, expiry_date_yyyymmdd: str, client_name: str = "") -> str:
    """
    Kriptografik HMAC imzoli Litsenziya Kalitini shakllantiradi.
    Format: ADV-<TIER>-<YYYYMMDD>-<HW8>-<SIG10>
    Masalan: ADV-SOLO-20271019-7A9B4C2F-A4B7C9D2E1
    """
    tier_clean = tier.strip().upper()
    ts_clean = expiry_date_yyyymmdd.replace("-", "").replace(".", "").strip()
    short_hw = hw_id.replace("UZ-ADV-", "").replace("-", "")[:8].upper()
    sig = _compute_signature(short_hw, tier_clean, ts_clean)
    return f"ADV-{tier_clean}-{ts_clean}-{short_hw}-{sig}"


def verify_license_key(key: str, hw_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Litsenziya kalitining haqiqiyligi, imzosi, apparat mosligi va muddatini tekshiradi.
    """
    if not key or not key.startswith("ADV-"):
        return {"valid": False, "error": "Litsenziya kaliti formati noto'g'ri (ADV- bilan boshlanishi shart)."}

    parts = key.strip().split("-")
    if len(parts) != 5:
        return {"valid": False, "error": "Kalit strukturasi buzilgan (5 ta qismdan iborat bo'lishi kerak)."}

    prefix, tier_str, ts_str, short_hw, sig = parts
    tier_key = tier_str.lower()
    current_hw = hw_id or get_hardware_fingerprint()
    curr_short = current_hw[:8].upper()

    # 1. Apparat ID mosligi (Enterprise uchun barcha kompyuterlarga ruxsat berilishi mumkin)
    if short_hw.upper() != curr_short and tier_str != "ENTERPRISE":
        return {
            "valid": False,
            "error": "Ushbu litsenziya kaliti boshqa kompyuterga bog'langan. Faqat kalit berilgan kompyuterda ishlaydi."
        }

    # 2. Kriptografik Imzo (HMAC) tekshiruvi
    expected_sig = _compute_signature(short_hw, tier_str, ts_str)
    if not hmac.compare_digest(sig.upper(), expected_sig):
        return {"valid": False, "error": "Litsenziya kaliti haqiqiy emas (kriptografik imzo xatosi)."}

    # 3. Muddat tekshiruvi (YYYYMMDD)
    try:
        exp_year = int(ts_str[:4])
        exp_month = int(ts_str[4:6])
        exp_day = int(ts_str[6:8])
        exp_date = datetime(exp_year, exp_month, exp_day, 23, 59, 59)
    except Exception:
        return {"valid": False, "error": "Litsenziya kalitidagi muddat formati noto'g'ri."}

    days_left = (exp_date - datetime.now()).days

    tier_info = TIERS.get(tier_key, TIERS["solo"])

    if datetime.now() > exp_date:
        return {
            "valid": False,
            "expired": True,
            "tier": tier_key,
            "tier_name": tier_info["name"],
            "hardware_id": current_hw,
            "expires_at": exp_date.strftime("%Y-%m-%d"),
            "days_left": 0,
            "error": f"Litsenziya muddati tugagan ({exp_date.strftime('%d.%m.%Y')}). Iltimos, litsenziyani yangilang."
        }

    return {
        "valid": True,
        "expired": False,
        "tier": tier_key,
        "tier_name": tier_info["name"],
        "badge": tier_info["badge"],
        "hardware_id": current_hw,
        "expires_at": exp_date.strftime("%Y-%m-%d"),
        "days_left": max(0, days_left),
        "features": tier_info["features"],
        "license_key": key
    }


def activate_license(key: str) -> Dict[str, Any]:
    """
    Foydalanuvchi kiritgan litsenziya kalitini faollashtiradi va doimiy faylga saqlaydi.
    """
    res = verify_license_key(key)
    if not res.get("valid"):
        return res

    lic_file = get_license_file()
    payload = {
        "license_key": key.strip(),
        "activated_at": datetime.now().isoformat(),
        "hardware_id": res["hardware_id"],
        "tier": res["tier"],
        "tier_name": res["tier_name"],
        "expires_at": res["expires_at"]
    }
    try:
        lic_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        return {"valid": False, "error": f"Litsenziyani saqlashda xatolik: {e}"}

    res["message"] = f"Litsenziya muvaffaqiyatli faollashtirildi! Tarif: {res['tier_name']}"
    return res


def get_current_license() -> Dict[str, Any]:
    """
    Amaldagi litsenziya holatini qaytaradi.
    Agar litsenziya bo'lmasa, birinchi marta avtomatik 14 kunlik Trial yaratiladi va saqlanadi.
    """
    current_hw = get_hardware_fingerprint()
    lic_file = get_license_file()

    if lic_file.exists():
        try:
            data = json.loads(lic_file.read_text(encoding="utf-8"))
            key = str(data.get("license_key", "")).strip()
            if key:
                verified = verify_license_key(key, current_hw)
                if verified.get("valid"):
                    return verified
                elif verified.get("expired"):
                    return verified
        except Exception:
            pass

    # Yangi kompyuter uchun 14 kunlik bepul sinov (Trial) ro'yxatdan o'tkazish
    trial_exp_str = (datetime.now() + timedelta(days=14)).strftime("%Y%m%d")
    trial_key = generate_license_key(current_hw, "trial", trial_exp_str, "Trial User")
    trial_payload = {
        "license_key": trial_key,
        "activated_at": datetime.now().isoformat(),
        "hardware_id": current_hw,
        "tier": "trial",
        "tier_name": "Sinov Davri (Trial 14 kun)",
        "expires_at": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    }
    try:
        lic_file.write_text(json.dumps(trial_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    return {
        "valid": True,
        "expired": False,
        "is_trial": True,
        "tier": "trial",
        "tier_name": "Sinov Davri (Trial 14 kun)",
        "badge": "SINOB (14 KUN)",
        "hardware_id": current_hw,
        "expires_at": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        "days_left": 14,
        "features": TIERS["trial"]["features"],
        "license_key": trial_key
    }


def is_feature_allowed(feature: str) -> Tuple[bool, str]:
    """
    Muayyan yuridik funksiyaga litsenziya ruxsat berishini tekshiradi.
    """
    lic = get_current_license()
    if not lic.get("valid"):
        err = lic.get("error", "Litsenziya muddati tugagan yoki faol emas.")
        return False, f"⚠️ {err} Iltimos, litsenziyani faollashtiring."

    allowed = lic.get("features", [])
    if "all" in allowed or feature in allowed:
        return True, ""
    return False, f"⚠️ Ushbu imkoniyat ('{feature}') sizning '{lic.get('tier_name')}' tarifingizda mavjud emas."


def generate_payment_links(tier: str, phone: str = "") -> Dict[str, str]:
    """
    Click va Payme orqali to'lov qilish uchun havolalarni shakllantiradi.
    """
    tier_info = TIERS.get(tier.lower(), TIERS["solo"])
    amount_uzs = tier_info["price_uzs"]
    amount_tiyin = amount_uzs * 100
    hw_id = get_hardware_fingerprint()
    order_id = f"ADV_{tier.upper()}_{int(time.time())}"

    # Click Checkout
    click_service_id = "32104"
    click_merchant_id = "21509"
    click_url = (
        f"https://my.click.uz/services/pay?service_id={click_service_id}&merchant_id={click_merchant_id}"
        f"&amount={amount_uzs}&transaction_param={order_id}&return_url=https://advokat-ai.uz/success"
    )

    # Payme Checkout
    payme_merchant_id = "64f9b8c9d1234567890abcdef"
    payme_url = (
        f"https://checkout.paycom.uz/{payme_merchant_id}?amount={amount_tiyin}"
        f"&account[order_id]={order_id}&account[hw_id]={hw_id}&account[phone]={phone}"
    )

    telegram_support = "https://t.me/AdvokatAI_Admin"

    return {
        "tier": tier,
        "tier_name": tier_info["name"],
        "price_uzs": amount_uzs,
        "order_id": order_id,
        "click_url": click_url,
        "payme_url": payme_url,
        "telegram_url": telegram_support
    }


def main():
    """Administrator / Sotuvchi uchun litsenziya kaliti yaratish CLI vositasi."""
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="ADVOKAT AI — Litsenziya Kaliti Generatori")
    parser.add_argument("--generate", action="store_true", help="Yangi litsenziya kalitini yaratish")
    parser.add_argument("--hwid", type=str, default="", help="Mijoz kompyuterining Apparat IDsi")
    parser.add_argument("--tier", type=str, default="solo", choices=["trial", "solo", "bureau", "enterprise"], help="Tarif rejasi")
    parser.add_argument("--days", type=int, default=365, help="Amal qilish muddati (kunlarda)")
    parser.add_argument("--name", type=str, default="Hurmatli Advokat", help="Mijoz F.I.Sh")
    parser.add_argument("--status", action="store_true", help="Joriy kompyuter litsenziyasi va apparat ID sini ko'rish")
    parser.add_argument("--activate", type=str, default="", help="Litsenziya kalitini faollashtirish")

    args = parser.parse_args()

    if args.status:
        hw = get_hardware_fingerprint()
        f_hw = get_formatted_hwid()
        lic = get_current_license()
        print("\n" + "=" * 60)
        print("🏛️ ADVOKAT AI — KOMPYUTER VA LITSENZIYA HOLATI")
        print("=" * 60)
        print(f"Kompyuter Apparat ID : {hw}")
        print(f"Formatlangan ID     : {f_hw}")
        print(f"Tarif               : {lic.get('tier_name')}")
        print(f"Holat               : {'FAOL ✅' if lic.get('valid') else 'MUDDATI OʻTGAN ❌'}")
        print(f"Tugash sanasi       : {lic.get('expires_at')} ({lic.get('days_left')} kun qoldi)")
        print(f"Litsenziya fayli    : {get_license_file()}")
        print("=" * 60 + "\n")
        return

    if args.activate:
        res = activate_license(args.activate)
        if res.get("valid"):
            print(f"✅ {res.get('message')}")
        else:
            print(f"❌ Xatolik: {res.get('error')}")
        return

    if args.generate:
        target_hw = args.hwid.strip() or get_hardware_fingerprint()
        target_hw_clean = target_hw.replace("UZ-ADV-", "").replace("-", "")[:8].upper()
        exp_date = (datetime.now() + timedelta(days=args.days)).strftime("%Y%m%d")
        key = generate_license_key(target_hw_clean, args.tier, exp_date, args.name)

        print("\n" + "=" * 65)
        print("🏛️ ADVOKAT AI — KRIPTOGRAFIK LITSENZIYA KALITI YARATILDI")
        print("=" * 65)
        print(f"Mijoz F.I.Sh        : {args.name}")
        print(f"Tarif rejasi        : {TIERS[args.tier]['name']} ({args.tier.upper()})")
        print(f"Amal qilish muddati : {args.days} kun ({(datetime.now() + timedelta(days=args.days)).strftime('%d.%m.%Y')} gacha)")
        print(f"Mijoz Kompyuter ID  : {target_hw}")
        print(f"Bog'langan qism     : {target_hw_clean}")
        print("-" * 65)
        print(f"🔑 LITSENZIYA KALITI:")
        print(f"    {key}")
        print("=" * 65)
        print("Ushbu kalitni mijozga yuboring. Dasturdagi [🔑 Litsenziya] oynasida faollashtiradi.\n")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
