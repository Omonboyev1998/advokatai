"""
Live Panels — the computer's vitals and the weather as live panels on the
HUD, drawn where the avatar sits and moving in real time.

    "show me the system status"      → rings for CPU, RAM, GPU and disk, sampled
    "how is my computer doing?"        every second; per-core load, a 60-second
                                       history, network speed, the heaviest
                                       processes
    "what's the weather in Tokyo?"   → now, the next 24 hours and seven days; the
    "show me the forecast"             local clock ticks, rain or snow falls
                                       behind it, the icons move
    "close it" / "close the panel"   → the HUD goes back to the avatar

THE PANELS ARE LIVE (_live_panels_core.py)
    Not pictures: they repaint while they are open and answer the mouse.
    System    click a ring to graph that metric, HISTORY / CORES to switch the
              left panel, a process for its PID, threads and start time; hover
              the graph to read any second.
    Weather   click a day to see its hours and details; hover the curve to read
              any hour. The data refreshes every ten minutes.
    The × in the corner closes a panel. Anything else taking the centre — a
    video, the camera, a picture — closes it too.

INSTALL
    Drop live_panels.py and _live_panels_core.py into plugins/ and restart. Nothing
    else changes: no key, no account. Uses psutil and PyQt6, which JARVIS already
    has; the weather comes from Open-Meteo (keyless). NVIDIA GPU load is read
    through NVML when the driver is there, and the GPU ring is left out otherwise.

NOTHING HERE KNOWS A LANGUAGE
    Results are facts — numbers and names as published — and the assistant says
    them in the user's language.
"""
from __future__ import annotations

import time
import types

PLUGIN = {
    "name": "live_panels",
    "description": (
        "Shows a LIVE, interactive panel on the HUD and returns the facts behind it. "
        "action='system': the computer's live diagnostics — CPU, RAM, GPU, disk, network, "
        "per-core load and the heaviest processes. action='weather': the weather for a city — "
        "now, the next 24 hours and 7 days (pass 'city'). action='close': close the panel. "
        "Prefer this over system_status for any question about the computer's performance, "
        "load, memory, disk or temperature, and over weather_report for any weather, "
        "temperature, rain or forecast question — it answers the same question AND shows the "
        "panel. Use action='close' when the user asks to close / hide the panel or dashboard."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "'system', 'weather' or 'close'",
            },
            "city": {
                "type": "STRING",
                "description": "City for action='weather', in any language",
            },
            "when": {
                "type": "STRING",
                "description": "What the user asked about for weather, e.g. 'today', 'tomorrow', 'weekend'",
            },
        },
        "required": ["action"],
    },
}


def _boards():
    try:
        from plugins import _live_panels_core as lb
    except ImportError:  # loaded outside the package
        import _live_panels_core as lb  # type: ignore
    return lb


def _log(player, text: str) -> None:
    print(f"[LivePanels] {text}")
    if player:
        try:
            player.write_log(f"JARVIS: {text}")
        except Exception:
            pass


def _hook_close(player, lb) -> None:
    """Make "close it" (the UI's stop_video) close the panels too — once, on this UI."""
    if player is None or getattr(player, "_live_panels_hooked", False):
        return
    original = getattr(player, "stop_video", None)
    if not callable(original):
        return

    def stop_video(self, *a, **kw):
        try:
            lb.close_all()
        except Exception:
            pass
        return original(*a, **kw)

    try:
        player.stop_video = types.MethodType(stop_video, player)
        player._live_panels_hooked = True
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Actions
# ─────────────────────────────────────────────────────────────────────────────

def _system(player, lb) -> str:
    import platform
    import psutil

    shown = bool(player) and lb.show_system(player)
    psutil.cpu_percent(None)
    time.sleep(0.4)
    cpu = psutil.cpu_percent(None)
    vm = psutil.virtual_memory()
    du = psutil.disk_usage("C:\\" if psutil.WINDOWS else "/")
    gpu = lb.gpu_load()
    up = time.time() - psutil.boot_time()
    facts = (
        f"CPU {cpu:.0f}%, RAM {vm.percent:.0f}% ({vm.used / 1024 ** 3:.1f} of "
        f"{vm.total / 1024 ** 3:.1f} GB), "
        + (f"GPU {gpu:.0f}%, " if gpu is not None else "")
        + f"disk {du.percent:.0f}% full ({du.free / 1024 ** 3:.0f} GB free), "
        f"uptime {int(up // 3600)}h {int(up % 3600 // 60)}m, {len(psutil.pids())} processes. "
        f"Machine: {platform.node()}. The busiest processes are listed on the panel."
    )
    _log(player, f"System: CPU {cpu:.0f}%, RAM {vm.percent:.0f}%")
    return (("A live diagnostics panel is now on the HUD (it updates every second; the user can "
             "click rings, tabs and processes). " if shown else "The panel could not be shown. ")
            + facts + " Answer briefly in the user's language; mention anything near its limit.")


def _weather(player, lb, city: str, when: str) -> str:
    if not city:
        return "status=ask question=which city the user wants the weather for"
    place = lb.geocode(city)
    if not place:
        return f"status=failed reason=no place called '{city}' was found"
    try:
        fc = lb.forecast(place["latitude"], place["longitude"])
    except Exception as e:
        return f"status=failed reason=Open-Meteo could not be reached ({type(e).__name__})"
    shown = bool(player) and lb.show_weather(player, place, fc)
    cur, day = fc["current"], fc["daily"]
    wmo = lb._WMO
    days = "; ".join(
        f"{day['time'][i]}: {wmo.get(day['weather_code'][i], ('?',))[0]}, "
        f"{round(day['temperature_2m_min'][i])}..{round(day['temperature_2m_max'][i])}°C, "
        f"rain {day['precipitation_probability_max'][i]}%"
        for i in range(len(day["time"])))
    _log(player, f"Weather for {place.get('name')}: {cur['temperature_2m']}°C")
    return (
        ("A live weather panel is now on the HUD (the user can click a day to see its hours). "
         if shown else "The panel could not be shown. ")
        + f"Weather for {place.get('name')}, {place.get('country', '')}. "
        f"Now: {wmo.get(cur['weather_code'], ('?',))[0]}, {cur['temperature_2m']}°C "
        f"(feels {cur['apparent_temperature']}°C), humidity {cur['relative_humidity_2m']}%, "
        f"wind {cur['wind_speed_10m']} km/h. Sunrise {day['sunrise'][0][-5:]}, "
        f"sunset {day['sunset'][0][-5:]}. The user asked about: {when or 'now'}. "
        f"7 days: {days}. Answer briefly in the user's language, focused on what they asked."
    )


def run(parameters: dict, player=None, session_memory=None) -> str:
    action = str(parameters.get("action") or "").strip().lower()
    city = str(parameters.get("city") or "").strip()
    when = str(parameters.get("when") or "").strip()
    if not action:
        action = "weather" if city else "system"
    try:
        lb = _boards()
        _hook_close(player, lb)
        if action in ("close", "hide", "stop"):
            lb.close_all()
            return "status=done closed=live panel"
        if action in ("weather", "forecast"):
            return _weather(player, lb, city, when)
        return _system(player, lb)
    except Exception as e:
        return f"status=failed reason=live_panels: {type(e).__name__}: {e}"
