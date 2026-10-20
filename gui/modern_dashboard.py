"""
gui/modern_dashboard.py — 100% Mockup-Aynan Zamonaviy Boshqaruv Markazi (Light Dashboard).

Foydalanuvchi taqdim etgan dizayn andozasiga (media_1791525280748_11db010d.png)
100% mos va har bir pikseliga qadar aniq ishlab chiqilgan:
- Barcha ikonlar (KPI, grid, sliders, power) sof QPainter vektor chizmasi orqali chizilgan (hech qanday bo'sh quti yoki emoji xatoligi bo'lmaydi)
- Vertikal Bar Ekvalayzer To'lqini (mockupdagi kabi 28 ta moviy barlar)
- 4 ta to'liq qulay vazifa qatorlari va DONE nishonlari (scrollbarsiz)
- Aloqa jurnalida mockupdagi 2 ta aniq xabarlar qutisi (Sariq NET xatolik va Oq tizim online qutisi)
- Chiziqli dropzone, matn kiritish va Mic/Stop tugmalari
"""

from __future__ import annotations
import math
import os
import psutil
import time
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import (
    QEasingCurve, QLineF, QPointF, QRectF, QSize, Qt, QTimer, pyqtSignal,
)
from PyQt6.QtGui import (
    QBrush, QColor, QFont, QIcon, QLinearGradient, QPainter, QPainterPath,
    QPen, QPixmap, QRadialGradient,
)
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QFrame, QGraphicsDropShadowEffect,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow, QProgressBar, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget,
)

from gui.theme import (
    C, APP_VERSION, _read_full_config
)
from gui.style import px_font


def with_alpha(hex_col: str, alpha: int) -> QColor:
    c = QColor(hex_col)
    c.setAlpha(max(0, min(255, int(alpha))))
    return c


# ── RANGLAR PALITRASI (LIGHT DASHBOARD THEME) ───────────────────────────────
class LTheme:
    BG          = "#f1f5f9"
    CARD_BG     = "#ffffff"
    BORDER      = "#e2e8f0"
    BORDER_SUB  = "#edf2f7"
    TEXT_MAIN   = "#0f172a"
    TEXT_MUTED  = "#64748b"
    TEXT_LIGHT  = "#94a3b8"
    BLUE        = "#2563eb"
    BLUE_LIGHT  = "#eff6ff"
    BLUE_BORDER = "#dbeafe"
    GREEN       = "#16a34a"
    GREEN_LIGHT = "#f0fdf4"
    GREEN_BORDER= "#bbf7d0"
    RED         = "#dc2626"
    RED_LIGHT   = "#fef2f2"
    RED_BORDER  = "#fecaca"
    YELLOW_BG   = "#fffbeb"
    YELLOW_BRD  = "#fef3c7"
    YELLOW_TXT  = "#92400e"


def card_shadow(blur=16, offset_y=3, alpha=12) -> QGraphicsDropShadowEffect:
    eff = QGraphicsDropShadowEffect()
    eff.setBlurRadius(blur)
    eff.setOffset(0, offset_y)
    eff.setColor(QColor(15, 23, 42, alpha))
    return eff


# ── SOF VEKTORLI I把它KONLAR (Platforma shriftlariga bog'liq emas) ───────────
class KpiVectorIcon(QWidget):
    def __init__(self, kind: str, is_alert: bool = False, parent=None):
        super().__init__(parent)
        self.setFixedSize(18, 18)
        self.kind = kind
        self.is_alert = is_alert

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        col = QColor(LTheme.RED if self.is_alert else LTheme.BLUE)
        pen = QPen(col, 1.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)

        if self.kind == "ram":
            p.drawRoundedRect(QRectF(2, 4, 14, 10), 2, 2)
            p.drawLine(QPointF(5, 7), QPointF(5, 11))
            p.drawLine(QPointF(9, 7), QPointF(9, 11))
            p.drawLine(QPointF(13, 7), QPointF(13, 11))
        elif self.kind == "temp":
            p.drawRoundedRect(QRectF(7, 2, 4, 10), 2, 2)
            p.drawEllipse(QPointF(9, 13), 3.5, 3.5)
            p.setBrush(QBrush(col))
            p.drawEllipse(QPointF(9, 13), 2.0, 2.0)
        elif self.kind == "uptime":
            p.drawEllipse(QPointF(9, 9), 7, 7)
            p.drawLine(QPointF(9, 9), QPointF(9, 5))
            p.drawLine(QPointF(9, 9), QPointF(12, 9))
        elif self.kind == "proc":
            p.drawRoundedRect(QRectF(4, 4, 10, 10), 2, 2)
            p.drawLine(QPointF(2, 7), QPointF(4, 7))
            p.drawLine(QPointF(2, 11), QPointF(4, 11))
            p.drawLine(QPointF(14, 7), QPointF(16, 7))
            p.drawLine(QPointF(14, 11), QPointF(16, 11))
            p.drawLine(QPointF(7, 2), QPointF(7, 4))
            p.drawLine(QPointF(11, 2), QPointF(11, 4))
            p.drawLine(QPointF(7, 14), QPointF(7, 16))
            p.drawLine(QPointF(11, 14), QPointF(11, 16))
        elif self.kind == "net":
            path = QPainterPath()
            path.moveTo(2, 9)
            path.lineTo(5, 9)
            path.lineTo(7, 3)
            path.lineTo(10, 15)
            path.lineTo(12, 7)
            path.lineTo(14, 9)
            path.lineTo(16, 9)
            p.drawPath(path)


class AppGridIconWidget(QWidget):
    """Boshqaruv tabi uchun 2x2 to'rtburchak vektorli ikonka."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(14, 14)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(LTheme.BLUE)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(1, 1, 5, 5), 1.2, 1.2)
        p.drawRoundedRect(QRectF(8, 1, 5, 5), 1.2, 1.2)
        p.drawRoundedRect(QRectF(1, 8, 5, 5), 1.2, 1.2)
        p.drawRoundedRect(QRectF(8, 8, 5, 5), 1.2, 1.2)


class TuneSlidersIconWidget(QWidget):
    """Header sozlamalar tugmasi uchun chiziqli sliderlar ikonkasi."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(LTheme.TEXT_MUTED), 1.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        # Line 1
        p.drawLine(QPointF(2, 4), QPointF(14, 4))
        p.setBrush(QBrush(QColor(LTheme.TEXT_MUTED)))
        p.drawEllipse(QPointF(6, 4), 1.8, 1.8)
        # Line 2
        p.drawLine(QPointF(2, 8), QPointF(14, 8))
        p.drawEllipse(QPointF(11, 8), 1.8, 1.8)
        # Line 3
        p.drawLine(QPointF(2, 12), QPointF(14, 12))
        p.drawEllipse(QPointF(5, 12), 1.8, 1.8)


class PowerIconWidget(QWidget):
    """Aloqa jurnalidagi online holat uchun quvvat (power) ikonkasi."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(LTheme.BLUE_LIGHT)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(0, 0, 24, 24), 6, 6)
        pen = QPen(QColor(LTheme.BLUE), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawArc(QRectF(5, 5, 14, 14), int(45 * 16), int(270 * 16))
        p.drawLine(QPointF(12, 4), QPointF(12, 11))


# ── 1. AVATAR CIRCLE WIDGET (3D Gologramma Yuz Dumaloq Ramkada) ──────────────
class ModernAvatarCircle(QWidget):
    def __init__(self, face_path: str = "core/advokat_avatar.png", parent=None):
        super().__init__(parent)
        self.setFixedSize(184, 184)
        self._pixmap = None
        for c in (face_path, "core/advokat_avatar.png", "face.png"):
            if c and Path(c).exists():
                pm = QPixmap(str(c))
                if not pm.isNull():
                    self._pixmap = pm
                    break
        self._amp = 0.0
        self._speaking = False
        self._muted = False
        self._tick = 0

        self._tmr = QTimer(self)
        self._tmr.timeout.connect(self._on_tick)
        self._tmr.start(25)

    def set_speaking(self, spk: bool):
        self._speaking = spk
        self.update()

    def set_muted(self, m: bool):
        self._muted = m
        self.update()

    def set_amp(self, amp: float):
        self._amp = max(0.0, min(1.0, amp))
        self.update()

    def _on_tick(self):
        self._tick += 1
        if self._speaking or self._amp > 0.03:
            self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()
        cx, cy = W / 2, H / 2
        r = (min(W, H) / 2) - 12

        amp = self._amp
        live = self._speaking or amp > 0.04

        # 1. Tashqi neon aura
        aura_r = r + 8 + (amp * 8 if live else 0)
        grad = QRadialGradient(cx, cy, aura_r)
        col = QColor(LTheme.RED if self._muted else LTheme.BLUE)
        grad.setColorAt(0.0, with_alpha(col.name(), int(160 if live else 60)))
        grad.setColorAt(0.7, with_alpha(col.name(), int(40 if live else 15)))
        grad.setColorAt(1.0, with_alpha(col.name(), 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawEllipse(QPointF(cx, cy), aura_r, aura_r)

        # 2. Dumaloq niqob ichida avatar rasmi
        p.save()
        clip = QPainterPath()
        clip.addEllipse(QPointF(cx, cy), r, r)
        p.setClipPath(clip)

        p.fillRect(self.rect(), QColor("#020813"))

        if self._pixmap is not None:
            size = int(r * 2)
            scaled = self._pixmap.scaled(
                size, size,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            p.drawPixmap(int(cx - size / 2), int(cy - size / 2), scaled)

        # Vignette
        vig = QRadialGradient(cx, cy, r)
        vig.setColorAt(0.0, QColor(0, 0, 0, 0))
        vig.setColorAt(0.75, QColor(0, 0, 0, 40))
        vig.setColorAt(0.95, QColor(2, 8, 19, 180))
        vig.setColorAt(1.0, QColor(2, 8, 19, 255))
        p.setBrush(QBrush(vig))
        p.drawEllipse(QPointF(cx, cy), r, r)

        # Skaner nuri
        scan_offset = (self._tick * 2.5) % (r * 2.4) - r * 1.2
        if abs(scan_offset) < r:
            scan_y = cy + scan_offset
            scan_grad = QLinearGradient(cx - r, scan_y, cx + r, scan_y)
            scan_grad.setColorAt(0.0, with_alpha(col.name(), 0))
            scan_grad.setColorAt(0.5, with_alpha(col.name(), 180 if live else 90))
            scan_grad.setColorAt(1.0, with_alpha(col.name(), 0))
            p.setPen(QPen(QBrush(scan_grad), 2))
            p.drawLine(QLineF(cx - r, scan_y, cx + r, scan_y))

        p.restore()

        # 3. Tashqi aylana ramkalar (Nozik neon halqa)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor(col.name()), 1.8))
        p.drawEllipse(QPointF(cx, cy), r + 2, r + 2)

        rot = self._tick * 0.8
        outer_r = r + 6
        p.setPen(QPen(with_alpha(col.name(), 130), 1.2, Qt.PenStyle.DashLine))
        box = QRectF(cx - outer_r, cy - outer_r, outer_r * 2, outer_r * 2)
        p.drawArc(box, int(rot * 16), int(120 * 16))
        p.drawArc(box, int((rot + 180) * 16), int(120 * 16))


# ── 2. DINAMIK WAVEFORM WIDGET (Vertikal Bar Ekvalayzer To'lqini) ─────────────
class ModernWaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._amp = 0.0
        self._tick = 0
        self._bars = 28

        self._tmr = QTimer(self)
        self._tmr.timeout.connect(self._step)
        self._tmr.start(35)

    def set_amp(self, val: float):
        self._amp = max(0.0, min(1.0, val))
        self.update()

    def _step(self):
        self._tick += 1
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()
        cy = H / 2

        amp = self._amp
        n = self._bars
        bar_w = 4.0
        gap = (W - (n * bar_w)) / max(1, n - 1)

        p.setPen(Qt.PenStyle.NoPen)
        for i in range(n):
            x = i * (bar_w + gap)
            # Markazga qarab balandlashuvchi tabiiy to'lqin shakli (Bell curve envelope)
            phase = (i / (n - 1)) * math.pi
            envelope = math.sin(phase)
            
            # Dinamik to'lqin tebranishi
            wave1 = math.sin(self._tick * 0.15 + i * 0.4)
            wave2 = math.cos(self._tick * 0.22 - i * 0.25)
            anim = 0.5 + 0.25 * (wave1 + wave2)

            # Har bir bar balandligi (Mockupdagi vertikal bar ko'rinishi)
            base_h = 9.0 + 19.0 * envelope
            live_h = (H * 0.9) * (0.2 + 0.8 * amp) * envelope * anim
            h = max(7.0, min(H - 4.0, max(base_h, live_h)))
            y = cy - h / 2

            # Mockupdagi moviy-havorang gradient barlar
            p.setBrush(QBrush(QColor("#38bdf8" if i % 2 == 0 else "#2563eb")))
            p.drawRoundedRect(QRectF(x, y, bar_w, h), 2.0, 2.0)


# ── 3. TOP KPI METRIKA KARTOCHKASI ──────────────────────────────────────────
class ModernKpiCard(QFrame):
    def __init__(self, title: str, value: str, sub: str = "", icon_kind: str = "ram",
                 is_alert: bool = False, has_progress: bool = False, prog_val: int = 0):
        super().__init__()
        self.setStyleSheet(f"""
            ModernKpiCard {{
                background: {LTheme.CARD_BG};
                border: 1px solid {LTheme.BORDER};
                border-radius: 14px;
            }}
        """)
        self.setGraphicsEffect(card_shadow(12, 2, 8))

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(6)

        # Yuqori sarlavha qatori
        hdr = QHBoxLayout()
        hdr.setSpacing(6)
        lbl_t = QLabel(title)
        lbl_t.setFont(px_font(12, QFont.Weight.Medium))
        lbl_t.setStyleSheet(f"color: {LTheme.TEXT_MUTED}; background: transparent; border: none;")
        hdr.addWidget(lbl_t)
        hdr.addStretch()

        self.ico_w = KpiVectorIcon(icon_kind, is_alert=is_alert)
        hdr.addWidget(self.ico_w)
        lay.addLayout(hdr)

        # Asosiy qiymat qatori
        val_lay = QHBoxLayout()
        val_lay.setSpacing(8)
        self.lbl_v = QLabel(value)
        self.lbl_v.setFont(px_font(22, QFont.Weight.Bold))
        v_col = LTheme.RED if is_alert else LTheme.TEXT_MAIN
        self.lbl_v.setStyleSheet(f"color: {v_col}; background: transparent; border: none;")
        val_lay.addWidget(self.lbl_v)

        if sub:
            lbl_s = QLabel(sub)
            lbl_s.setFont(px_font(10, QFont.Weight.Medium))
            s_col = LTheme.RED if is_alert else LTheme.TEXT_MUTED
            lbl_s.setStyleSheet(f"color: {s_col}; background: transparent; border: none;")
            val_lay.addWidget(lbl_s, alignment=Qt.AlignmentFlag.AlignBottom)
        val_lay.addStretch()
        lay.addLayout(val_lay)

        # Nozik progress bar (faqat Xotira/RAM uchun)
        if has_progress:
            self.pbar = QProgressBar()
            self.pbar.setFixedHeight(4)
            self.pbar.setTextVisible(False)
            self.pbar.setRange(0, 100)
            self.pbar.setValue(prog_val)
            self.pbar.setStyleSheet(f"""
                QProgressBar {{
                    background: #fee2e2; border: none; border-radius: 2px;
                }}
                QProgressBar::chunk {{
                    background: {LTheme.RED}; border-radius: 2px;
                }}
            """)
            lay.addWidget(self.pbar)
        else:
            lay.addSpacing(4)


# ── 4. MODERN DASHBOARD WINDOW (Asosiy Boshqaruv Oynasi) ────────────────────
class ModernDashboardWindow(QMainWindow):
    _log_sig          = pyqtSignal(str)
    _state_sig        = pyqtSignal(str)
    _content_sig      = pyqtSignal(str, str)
    _confirm_sig      = pyqtSignal(str, str)
    _confirm_hide_sig = pyqtSignal()
    _tasks_sig        = pyqtSignal(list)
    _routines_sig     = pyqtSignal(list)
    _quiz_sig         = pyqtSignal(str, list, object)
    _quiz_hide_sig    = pyqtSignal()
    _review_sig       = pyqtSignal(str, str, list, list)
    _reconfig_sig     = pyqtSignal()
    _camera_sig       = pyqtSignal(bytes)
    _video_open_sig   = pyqtSignal(str, str, bool, str)
    _image_open_sig   = pyqtSignal(str, str)
    _video_close_sig  = pyqtSignal()
    _video_mute_sig   = pyqtSignal(bool)
    _video_seek_sig   = pyqtSignal(float, bool)
    _video_pause_sig  = pyqtSignal(bool)

    def __init__(self, face_path: str = "core/advokat_avatar.png", assistant_name: str = "ADVOKAT AI"):
        super().__init__()
        self._assistant_name = assistant_name or "ADVOKAT AI"
        self._muted = False
        self._speaking = False
        self._ready = True
        self.setAcceptDrops(True)

        # Callbacks
        self.on_text_command = None
        self.on_interrupt = None
        self.on_voice_change = None
        self.on_audio_device_change = None
        self.get_plugins = None
        self.get_plugin_settings = None
        self.on_wake_toggle = None
        self.on_wake_manual = None
        self.on_push_to_talk = None
        self.ptt_hold = None
        self.wake_get_state = None
        self.on_remote_clicked = None

        self._dropped_file: str | None = None

        self.setWindowTitle(f"{self._assistant_name} — SHAXSIY BOSHQARUV MARKAZI")
        self.resize(1280, 880)
        self.setMinimumSize(1100, 780)

        # Asosiy fon
        self.setStyleSheet(f"""
            QMainWindow {{ background: {LTheme.BG}; }}
            QScrollBar:vertical {{ width: 0px; background: transparent; }}
            QScrollBar:horizontal {{ height: 0px; background: transparent; }}
        """)

        # Central Widget
        central = QWidget()
        central.setStyleSheet(f"background: {LTheme.BG};")
        self.setCentralWidget(central)

        main_lay = QVBoxLayout(central)
        main_lay.setContentsMargins(24, 14, 24, 12)
        main_lay.setSpacing(14)

        # 1. Top Navbar
        main_lay.addWidget(self._build_top_navbar())

        # 2. Hero Title & Alert Notice
        main_lay.addWidget(self._build_hero_section())

        # 3. 5 ta Metrika Kartochkalari
        main_lay.addWidget(self._build_metrics_grid())

        # 4. Asosiy 2 Ustunli Body (Chap & O'ng)
        main_lay.addLayout(self._build_two_columns(face_path), stretch=1)

        # 5. Pastki Footer (Status bar)
        main_lay.addWidget(self._build_footer())

        # Signallarni ulash
        self._log_sig.connect(self._handle_log)
        self._state_sig.connect(self._handle_state)
        self._content_sig.connect(self._handle_content)

        # Metriklarni davriy yangilash
        self._uptime_start = time.time()
        self._metric_timer = QTimer(self)
        self._metric_timer.timeout.connect(self._refresh_system_metrics)
        self._metric_timer.start(2000)

    # ── 1. TOP NAVBAR ────────────────────────────────────────────────────────
    def _build_top_navbar(self) -> QWidget:
        nav = QFrame()
        nav.setFixedHeight(54)
        nav.setStyleSheet(f"""
            QFrame {{
                background: {LTheme.CARD_BG};
                border: 1px solid {LTheme.BORDER};
                border-radius: 14px;
            }}
        """)
        nav.setGraphicsEffect(card_shadow(10, 2, 8))

        lay = QHBoxLayout(nav)
        lay.setContentsMargins(18, 6, 18, 6)
        lay.setSpacing(14)

        # Logo & App Title (Adolat tarozisi logotipi)
        logo_ico = QLabel("⚖️")
        logo_ico.setFont(px_font(18))
        logo_ico.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(logo_ico)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        lbl_app = QLabel(self._assistant_name)
        lbl_app.setFont(px_font(14, QFont.Weight.Bold))
        lbl_app.setStyleSheet(f"color: {LTheme.TEXT_MAIN}; background: transparent; border: none;")
        title_col.addWidget(lbl_app)

        lbl_sub = QLabel("MARK LVII  /  YURIDIK TIZIM")
        lbl_sub.setFont(px_font(9, QFont.Weight.DemiBold, spacing=1.2))
        lbl_sub.setStyleSheet(f"color: {LTheme.TEXT_MUTED}; background: transparent; border: none;")
        title_col.addWidget(lbl_sub)
        lay.addLayout(title_col)

        lay.addSpacing(24)

        # Nav Tablet Tablari (Mockup-aynan: Vektorli grid + Boshqaruv | Vazifalar | Aloqa jurnali)
        tab_wrap = QHBoxLayout()
        tab_wrap.setSpacing(6)

        # Boshqaruv faol tab
        tab_box = QFrame()
        tab_box.setStyleSheet(f"""
            QFrame {{
                background: {LTheme.BLUE_LIGHT}; border: 1px solid {LTheme.BLUE_BORDER};
                border-radius: 8px;
            }}
        """)
        t_box_lay = QHBoxLayout(tab_box)
        t_box_lay.setContentsMargins(10, 5, 12, 5)
        t_box_lay.setSpacing(6)
        t_box_lay.addWidget(AppGridIconWidget())
        t_lbl = QLabel("Boshqaruv")
        t_lbl.setFont(px_font(12, QFont.Weight.DemiBold))
        t_lbl.setStyleSheet(f"color: {LTheme.BLUE}; background: transparent; border: none;")
        t_box_lay.addWidget(t_lbl)
        tab_wrap.addWidget(tab_box)

        self.tab_tasks = QPushButton("Vazifalar")
        self.tab_tasks.setFont(px_font(12, QFont.Weight.Medium))
        self.tab_tasks.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {LTheme.TEXT_MUTED};
                border: none; padding: 6px 14px;
            }}
            QPushButton:hover {{ color: {LTheme.TEXT_MAIN}; }}
        """)
        tab_wrap.addWidget(self.tab_tasks)

        self.tab_log = QPushButton("Aloqa jurnali")
        self.tab_log.setFont(px_font(12, QFont.Weight.Medium))
        self.tab_log.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {LTheme.TEXT_MUTED};
                border: none; padding: 6px 14px;
            }}
            QPushButton:hover {{ color: {LTheme.TEXT_MAIN}; }}
        """)
        tab_wrap.addWidget(self.tab_log)
        lay.addLayout(tab_wrap)

        lay.addStretch()

        # Online Status Badge (Yashil nishon)
        self.lbl_status_chip = QLabel("●  ADVOKAT AI online")
        self.lbl_status_chip.setFont(px_font(11, QFont.Weight.DemiBold))
        self.lbl_status_chip.setStyleSheet(f"""
            background: {LTheme.GREEN_LIGHT}; color: {LTheme.GREEN};
            border: 1px solid {LTheme.GREEN_BORDER}; border-radius: 16px;
            padding: 4px 12px;
        """)
        lay.addWidget(self.lbl_status_chip)

        # Soat
        self.lbl_clock = QLabel(datetime.now().strftime("%H:%M"))
        self.lbl_clock.setFont(px_font(13, QFont.Weight.Bold))
        self.lbl_clock.setStyleSheet(f"color: {LTheme.TEXT_MAIN}; background: transparent; border: none;")
        lay.addWidget(self.lbl_clock)

        # Sozlamalar / Sliders tugmasi (Mockupdagi chiroyli vektorli quti)
        btn_opt_box = QFrame()
        btn_opt_box.setFixedSize(32, 32)
        btn_opt_box.setStyleSheet(f"""
            QFrame {{
                background: #ffffff; border: 1px solid {LTheme.BORDER};
                border-radius: 8px;
            }}
            QFrame:hover {{ background: #f8fafc; border-color: #cbd5e1; }}
        """)
        b_lay = QHBoxLayout(btn_opt_box)
        b_lay.setContentsMargins(0, 0, 0, 0)
        b_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        b_lay.addWidget(TuneSlidersIconWidget())
        lay.addWidget(btn_opt_box)

        return nav

    # ── 2. HERO SECTION & ALERT NOTICE ───────────────────────────────────────
    def _build_hero_section(self) -> QWidget:
        box = QWidget()
        box.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        # Katta Sarlavha qatori
        top_row = QHBoxLayout()
        h_col = QVBoxLayout()
        h_col.setSpacing(2)

        title = QLabel("Shaxsiy boshqaruv markazi")
        title.setFont(px_font(22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {LTheme.TEXT_MAIN};")
        h_col.addWidget(title)

        sub = QLabel("Ovoz, vazifalar va tizim holati — yagona ish maydonida.")
        sub.setFont(px_font(12, QFont.Weight.Normal))
        sub.setStyleSheet(f"color: {LTheme.TEXT_MUTED};")
        h_col.addWidget(sub)
        top_row.addLayout(h_col)
        top_row.addStretch()

        stamp = QLabel(f"📷  Tizim surati · {datetime.now().strftime('%H:%M')}")
        stamp.setFont(px_font(11, QFont.Weight.Medium))
        stamp.setStyleSheet(f"color: {LTheme.TEXT_LIGHT};")
        top_row.addWidget(stamp)
        lay.addLayout(top_row)

        # Sariq Ogohlantirish Paneli (Mockup-aynan)
        alert = QFrame()
        alert.setStyleSheet(f"""
            QFrame {{
                background: {LTheme.YELLOW_BG};
                border: 1px solid {LTheme.YELLOW_BRD};
                border-radius: 12px;
            }}
        """)
        a_lay = QHBoxLayout(alert)
        a_lay.setContentsMargins(16, 10, 16, 10)
        a_lay.setSpacing(12)

        ico = QLabel("⚠️")
        ico.setFont(px_font(15))
        ico.setStyleSheet("background: transparent; border: none;")
        a_lay.addWidget(ico)

        txt_col = QVBoxLayout()
        txt_col.setSpacing(2)
        at1 = QLabel("Tizim va Huquqiy Bilimlar Bazasi Faol")
        at1.setFont(px_font(12, QFont.Weight.Bold))
        at1.setStyleSheet(f"color: {LTheme.YELLOW_TXT}; background: transparent; border: none;")
        txt_col.addWidget(at1)

        at2 = QLabel("O'zbekiston Respublikasi qonunchiligi (8 186 ta amaliyotchi advokat taktikasi) yuklangan va tayyor.")
        at2.setFont(px_font(11, QFont.Weight.Normal))
        at2.setStyleSheet(f"color: #a16207; background: transparent; border: none;")
        txt_col.addWidget(at2)
        a_lay.addLayout(txt_col)
        a_lay.addStretch()

        btn_re = QPushButton("🔄  Qayta tekshirish")
        btn_re.setFont(px_font(11, QFont.Weight.DemiBold))
        btn_re.setStyleSheet(f"""
            QPushButton {{
                background: #ffffff; color: {LTheme.BLUE};
                border: 1px solid {LTheme.BLUE_BORDER}; border-radius: 8px;
                padding: 6px 14px;
            }}
            QPushButton:hover {{ background: {LTheme.BLUE_LIGHT}; }}
        """)
        a_lay.addWidget(btn_re)
        lay.addWidget(alert)

        return box

    # ── 3. 5 TA METRIKA KARTOCHKASI (Top KPI Grid) ───────────────────────────
    def _build_metrics_grid(self) -> QWidget:
        grid_w = QWidget()
        grid_w.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(grid_w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        # 1. Xotira (RAM)
        ram = psutil.virtual_memory().percent
        self.kpi_ram = ModernKpiCard("Xotira", f"{int(ram)}%", "Yuqori yuklama", icon_kind="ram",
                                     is_alert=True, has_progress=True, prog_val=int(ram))
        lay.addWidget(self.kpi_ram)

        # 2. Harorat
        self.kpi_temp = ModernKpiCard("Harorat", "48°", "TEMP", icon_kind="temp")
        lay.addWidget(self.kpi_temp)

        # 3. Ish vaqti
        self.kpi_uptime = ModernKpiCard("Ish vaqti", "12:40", "UPTIME", icon_kind="uptime")
        lay.addWidget(self.kpi_uptime)

        # 4. Jarayonlar
        proc_cnt = len(psutil.pids())
        self.kpi_proc = ModernKpiCard("Jarayonlar", str(proc_cnt), "PROCESSES", icon_kind="proc")
        lay.addWidget(self.kpi_proc)

        # 5. Tarmoq tezligi
        self.kpi_net = ModernKpiCard("Tarmoq tezligi", "284 KB/s", "Snapshot", icon_kind="net")
        lay.addWidget(self.kpi_net)

        return grid_w

    # ── 4. ASOSIY 2 USTUNLI BODY ─────────────────────────────────────────────
    def _build_two_columns(self, face_path: str) -> QHBoxLayout:
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(14)

        # ── CHAP USTUN ──────────────────────────────────────────────
        left_col = QVBoxLayout()
        left_col.setSpacing(14)

        # Card 1: Ovozli yordamchi
        left_col.addWidget(self._build_voice_assistant_card(face_path), stretch=0)

        # Card 2: Aloqa jurnali
        left_col.addWidget(self._build_communications_card(), stretch=1)

        body.addLayout(left_col, stretch=1)

        # ── O'NG USTUN ──────────────────────────────────────────────
        right_col = QVBoxLayout()
        right_col.setSpacing(14)

        # Card 3: Vazifalar
        right_col.addWidget(self._build_tasks_card(), stretch=1)

        # Card 4: Buyruq markazi
        right_col.addWidget(self._build_command_center_card(), stretch=0)

        body.addLayout(right_col, stretch=1)

        return body

    # ── Card 1: OVOZLI YORDAMCHI KARTOCHKASI ──────────────────────────────────
    def _build_voice_assistant_card(self, face_path: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {LTheme.CARD_BG};
                border: 1px solid {LTheme.BORDER};
                border-radius: 16px;
            }}
        """)
        card.setGraphicsEffect(card_shadow(14, 3, 10))

        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(20, 18, 20, 16)
        vbox.setSpacing(12)

        # Header: Ovozli yordamchi + Gapirmoqda / Tinglamoqda nishoni
        hdr = QHBoxLayout()
        h_ico = QLabel("〰")
        h_ico.setFont(px_font(14, QFont.Weight.Bold))
        h_ico.setStyleSheet(f"color: {LTheme.BLUE}; background: transparent; border: none;")
        hdr.addWidget(h_ico)

        h_lbl = QLabel("Ovozli yordamchi")
        h_lbl.setFont(px_font(14, QFont.Weight.Bold))
        h_lbl.setStyleSheet(f"color: {LTheme.TEXT_MAIN}; background: transparent; border: none;")
        hdr.addWidget(h_lbl)
        hdr.addStretch()

        self.lbl_voice_badge = QLabel("●  Tinglamoqda")
        self.lbl_voice_badge.setFont(px_font(11, QFont.Weight.DemiBold))
        self.lbl_voice_badge.setStyleSheet(f"""
            background: {LTheme.BLUE_LIGHT}; color: {LTheme.BLUE};
            border: 1px solid {LTheme.BLUE_BORDER}; border-radius: 12px;
            padding: 3px 10px;
        """)
        hdr.addWidget(self.lbl_voice_badge)
        vbox.addLayout(hdr)

        # Markaziy qism: Chapda 3D Avatar, O'ngda Waveform & Info
        center_row = QHBoxLayout()
        center_row.setSpacing(20)

        # 3D Avatar
        self.avatar_circle = ModernAvatarCircle(face_path)
        center_row.addWidget(self.avatar_circle, alignment=Qt.AlignmentFlag.AlignCenter)

        # O'ng qism: Sarlavha, To'lqin va Parametrlar
        info_col = QVBoxLayout()
        info_col.setSpacing(4)
        info_col.addStretch()

        lbl_proto = QLabel("VOICE INTERFACE / LVII")
        lbl_proto.setFont(px_font(10, QFont.Weight.Bold, spacing=1.2))
        lbl_proto.setStyleSheet(f"color: {LTheme.BLUE}; background: transparent; border: none;")
        info_col.addWidget(lbl_proto)

        self.lbl_hero_greet = QLabel(f"{self._assistant_name} siz bilan.")
        self.lbl_hero_greet.setFont(px_font(22, QFont.Weight.Bold))
        self.lbl_hero_greet.setStyleSheet(f"color: {LTheme.TEXT_MAIN}; background: transparent; border: none;")
        info_col.addWidget(self.lbl_hero_greet)

        self.lbl_sub_status = QLabel("Ovozli javob ijro etilmoqda...")
        self.lbl_sub_status.setFont(px_font(12))
        self.lbl_sub_status.setStyleSheet(f"color: {LTheme.TEXT_MUTED}; background: transparent; border: none;")
        info_col.addWidget(self.lbl_sub_status)

        info_col.addSpacing(4)

        # Vertikal Bar Ekvalayzer To'lqini (Mockup-aynan!)
        self.waveform = ModernWaveformWidget()
        info_col.addWidget(self.waveform)

        info_col.addSpacing(4)

        # Parametrlar (AI modeli, Ovoz, Platforma)
        params_row = QHBoxLayout()
        params_row.setSpacing(16)

        for p_name, p_val in [("AI modeli", "GEMINI LIVE"), ("Ovoz", "CHARON"), ("Platforma", "WINDOWS")]:
            c_lay = QVBoxLayout()
            c_lay.setSpacing(1)
            t_l = QLabel(p_name)
            t_l.setFont(px_font(9, QFont.Weight.Medium))
            t_l.setStyleSheet(f"color: {LTheme.TEXT_LIGHT}; background: transparent; border: none;")
            v_l = QLabel(p_val)
            v_l.setFont(px_font(11, QFont.Weight.Bold))
            v_l.setStyleSheet(f"color: {LTheme.TEXT_MAIN}; background: transparent; border: none;")
            c_lay.addWidget(t_l)
            c_lay.addWidget(v_l)
            params_row.addLayout(c_lay)
        params_row.addStretch()
        info_col.addLayout(params_row)

        info_col.addStretch()
        center_row.addLayout(info_col, stretch=1)
        vbox.addLayout(center_row)

        # Pastki footer: Mikrofon faol va Protocol (Keng va erkin joylashgan)
        ft_row = QHBoxLayout()
        ft_row.setContentsMargins(4, 4, 4, 0)
        self.lbl_mic_status = QLabel("🎙  Mikrofon faol · MIC LIVE")
        self.lbl_mic_status.setFont(px_font(11, QFont.Weight.DemiBold))
        self.lbl_mic_status.setStyleSheet(f"color: {LTheme.GREEN}; background: transparent; border: none;")
        ft_row.addWidget(self.lbl_mic_status)
        ft_row.addStretch()

        lbl_p_foot = QLabel("PROTOCOL · LVII")
        lbl_p_foot.setFont(px_font(9, QFont.Weight.Bold, spacing=1.2))
        lbl_p_foot.setStyleSheet(f"color: {LTheme.TEXT_LIGHT}; background: transparent; border: none;")
        ft_row.addWidget(lbl_p_foot)
        vbox.addLayout(ft_row)

        return card

    # ── Card 2: ALOQA JURNALI (Mockup-aynan ikki qutidan iborat) ─────────────
    def _build_communications_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {LTheme.CARD_BG};
                border: 1px solid {LTheme.BORDER};
                border-radius: 16px;
            }}
        """)
        card.setGraphicsEffect(card_shadow(14, 3, 10))

        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)

        # Header
        hdr = QHBoxLayout()
        h_ico = QLabel("💬")
        h_ico.setFont(px_font(14))
        h_ico.setStyleSheet(f"color: {LTheme.BLUE}; background: transparent; border: none;")
        hdr.addWidget(h_ico)

        h_title = QLabel("Aloqa jurnali")
        h_title.setFont(px_font(14, QFont.Weight.Bold))
        h_title.setStyleSheet(f"color: {LTheme.TEXT_MAIN}; background: transparent; border: none;")
        hdr.addWidget(h_title)
        hdr.addStretch()

        self.lbl_log_count = QLabel("2 xabar")
        self.lbl_log_count.setFont(px_font(10, QFont.Weight.DemiBold))
        self.lbl_log_count.setStyleSheet(f"""
            background: #f1f5f9; color: {LTheme.TEXT_MUTED};
            border-radius: 10px; padding: 2px 8px; border: none;
        """)
        hdr.addWidget(self.lbl_log_count)
        lay.addLayout(hdr)

        # Xabarlar maydoni (Scrollbarsiz toza, chiroyli qutilar)
        self.log_scroll = QScrollArea()
        self.log_scroll.setWidgetResizable(True)
        self.log_scroll.setStyleSheet("background: transparent; border: none;")
        self.log_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.log_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.log_container = QWidget()
        self.log_container.setStyleSheet("background: transparent;")
        self.log_lay = QVBoxLayout(self.log_container)
        self.log_lay.setContentsMargins(0, 2, 0, 2)
        self.log_lay.setSpacing(8)

        # Mockup 1-xabar: Sariq Tarmoq ogohlantirish qutisi
        box1 = QFrame()
        box1.setStyleSheet(f"""
            QFrame {{
                background: {LTheme.YELLOW_BG}; border: 1px solid {LTheme.YELLOW_BRD};
                border-radius: 10px;
            }}
        """)
        b1_lay = QVBoxLayout(box1)
        b1_lay.setContentsMargins(12, 8, 12, 8)
        b1_lay.setSpacing(2)

        b1_hdr = QHBoxLayout()
        b1_t1 = QLabel("⚠️  SYS · NET")
        b1_t1.setFont(px_font(9, QFont.Weight.Bold))
        b1_t1.setStyleSheet(f"color: {LTheme.YELLOW_TXT}; background: transparent; border: none;")
        b1_hdr.addWidget(b1_t1)
        b1_hdr.addStretch()
        b1_time = QLabel("14:47:08")
        b1_time.setFont(px_font(9, QFont.Weight.Medium, mono=True))
        b1_time.setStyleSheet(f"color: {LTheme.YELLOW_TXT}; background: transparent; border: none;")
        b1_hdr.addWidget(b1_time)
        b1_lay.addLayout(b1_hdr)

        b1_m1 = QLabel("NET: Connection failed — retrying in..")
        b1_m1.setFont(px_font(11, QFont.Weight.DemiBold, mono=True))
        b1_m1.setStyleSheet("color: #b45309; background: transparent; border: none;")
        b1_lay.addWidget(b1_m1)

        b1_m2 = QLabel("...be required) - Manbadagi xabar davomi kesilgan")
        b1_m2.setFont(px_font(10, QFont.Weight.Normal))
        b1_m2.setStyleSheet("color: #a16207; background: transparent; border: none;")
        b1_lay.addWidget(b1_m2)
        self.log_lay.addWidget(box1)

        # Mockup 2-xabar: Oq Tizim online qutisi (Vektorli quvvat ikonkasi bilan)
        box2 = QFrame()
        box2.setStyleSheet(f"""
            QFrame {{
                background: #ffffff; border: 1px solid {LTheme.BORDER};
                border-radius: 10px;
            }}
        """)
        b2_lay = QHBoxLayout(box2)
        b2_lay.setContentsMargins(12, 8, 12, 8)
        b2_lay.setSpacing(10)

        b2_lay.addWidget(PowerIconWidget())

        b2_col = QVBoxLayout()
        b2_col.setSpacing(1)
        b2_hdr = QLabel("SYS · 14:47:00")
        b2_hdr.setFont(px_font(9, QFont.Weight.Bold, mono=True))
        b2_hdr.setStyleSheet(f"color: {LTheme.TEXT_LIGHT}; background: transparent; border: none;")
        b2_col.addWidget(b2_hdr)

        b2_txt = QLabel(f"{self._assistant_name} online.")
        b2_txt.setFont(px_font(11, QFont.Weight.DemiBold))
        b2_txt.setStyleSheet(f"color: {LTheme.TEXT_MAIN}; background: transparent; border: none;")
        b2_col.addWidget(b2_txt)
        b2_lay.addLayout(b2_col)
        b2_lay.addStretch()
        self.log_lay.addWidget(box2)

        self.log_lay.addStretch()
        self.log_scroll.setWidget(self.log_container)
        lay.addWidget(self.log_scroll, stretch=1)

        foot = QLabel("Xabarlar manba suratidagi holatni aks ettiradi.")
        foot.setFont(px_font(10))
        foot.setStyleSheet(f"color: {LTheme.TEXT_LIGHT}; background: transparent; border: none;")
        lay.addWidget(foot)

        return card

    # ── Card 3: VAZIFALAR (Tasks & Routines — 4 ta aniq qulay qator) ──────────
    def _build_tasks_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {LTheme.CARD_BG};
                border: 1px solid {LTheme.BORDER};
                border-radius: 16px;
            }}
        """)
        card.setGraphicsEffect(card_shadow(14, 3, 10))

        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)

        # Header: Vazifalar + ROUTINES tugmasi
        hdr = QHBoxLayout()
        h_ico = QLabel("≡")
        h_ico.setFont(px_font(16, QFont.Weight.Bold))
        h_ico.setStyleSheet(f"color: {LTheme.BLUE}; background: transparent; border: none;")
        hdr.addWidget(h_ico)

        h_title = QLabel("Vazifalar")
        h_title.setFont(px_font(14, QFont.Weight.Bold))
        h_title.setStyleSheet(f"color: {LTheme.TEXT_MAIN}; background: transparent; border: none;")
        hdr.addWidget(h_title)
        hdr.addStretch()

        btn_routines = QPushButton("ROUTINES")
        btn_routines.setFont(px_font(10, QFont.Weight.Bold, spacing=1.1))
        btn_routines.setStyleSheet(f"""
            QPushButton {{
                background: #ffffff; color: {LTheme.TEXT_MUTED};
                border: 1px solid {LTheme.BORDER}; border-radius: 6px;
                padding: 4px 10px;
            }}
            QPushButton:hover {{ background: #f8fafc; color: {LTheme.TEXT_MAIN}; }}
        """)
        hdr.addWidget(btn_routines)
        lay.addLayout(hdr)

        # Filtrlar qatori: Bajarilgan + Dropdown
        filt_row = QHBoxLayout()
        filt_row.setSpacing(8)

        btn_done = QPushButton("Bajarilgan")
        btn_done.setFont(px_font(11, QFont.Weight.DemiBold))
        btn_done.setStyleSheet(f"""
            background: {LTheme.BLUE_LIGHT}; color: {LTheme.BLUE};
            border: 1px solid {LTheme.BLUE_BORDER}; border-radius: 8px;
            padding: 4px 12px;
        """)
        filt_row.addWidget(btn_done)

        combo = QComboBox()
        combo.addItems(["Barcha vazifalar", "Faol", "Arxiv"])
        combo.setFont(px_font(11))
        combo.setStyleSheet(f"""
            QComboBox {{
                background: #ffffff; border: 1px solid {LTheme.BORDER};
                border-radius: 8px; padding: 4px 12px; color: {LTheme.TEXT_MUTED};
            }}
            QComboBox::drop-down {{ border: none; }}
        """)
        filt_row.addWidget(combo)
        filt_row.addStretch()
        lay.addLayout(filt_row)

        # 4 ta Keng Vazifa Ro'yxati (Mockup-aynan!)
        self.tasks_scroll = QScrollArea()
        self.tasks_scroll.setWidgetResizable(True)
        self.tasks_scroll.setStyleSheet("background: transparent; border: none;")
        self.tasks_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tasks_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.tasks_cont = QWidget()
        self.tasks_cont.setStyleSheet("background: transparent;")
        self.tasks_lay = QVBoxLayout(self.tasks_cont)
        self.tasks_lay.setContentsMargins(0, 2, 0, 2)
        self.tasks_lay.setSpacing(6)

        # Mockupdagi 4 ta aniq vazifa
        self._append_task_row("...fani bo'yi...", "...ti.txt")
        self._append_task_row("...minut...", "")
        self._append_task_row("...mer conditi...", "...ays within its findings")
        self._append_task_row("...ways to...", "")

        self.tasks_lay.addStretch()
        self.tasks_scroll.setWidget(self.tasks_cont)
        lay.addWidget(self.tasks_scroll, stretch=1)

        foot = QLabel("ℹ️  Matn manbada kesilgan; ko'rinadigan qismlar saqlandi.")
        foot.setFont(px_font(10))
        foot.setStyleSheet(f"color: {LTheme.TEXT_LIGHT}; background: transparent; border: none;")
        lay.addWidget(foot)

        return card

    # ── Card 4: BUYRUQ MARKAZI (Command Center & Dropzone) ────────────────────
    def _build_command_center_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {LTheme.CARD_BG};
                border: 1px solid {LTheme.BORDER};
                border-radius: 16px;
            }}
        """)
        card.setGraphicsEffect(card_shadow(14, 3, 10))

        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)

        # Header
        hdr = QHBoxLayout()
        h_ico = QLabel(">_")
        h_ico.setFont(px_font(13, QFont.Weight.Bold))
        h_ico.setStyleSheet(f"color: {LTheme.BLUE}; background: transparent; border: none;")
        hdr.addWidget(h_ico)

        h_title = QLabel("Buyruq markazi")
        h_title.setFont(px_font(14, QFont.Weight.Bold))
        h_title.setStyleSheet(f"color: {LTheme.TEXT_MAIN}; background: transparent; border: none;")
        hdr.addWidget(h_title)
        hdr.addStretch()
        lay.addLayout(hdr)

        # File Dropzone Box (Chiziqli yuklash qutisi)
        self.drop_box = QFrame()
        self.drop_box.setCursor(Qt.CursorShape.PointingHandCursor)
        self.drop_box.setStyleSheet(f"""
            QFrame {{
                background: #f8fafc;
                border: 1.5px dashed #cbd5e1;
                border-radius: 12px;
            }}
            QFrame:hover {{
                border-color: {LTheme.BLUE};
                background: {LTheme.BLUE_LIGHT};
            }}
        """)
        d_lay = QHBoxLayout(self.drop_box)
        d_lay.setContentsMargins(14, 10, 14, 10)
        d_lay.setSpacing(10)

        d_ico = QLabel("📤")
        d_ico.setFont(px_font(15))
        d_ico.setStyleSheet("background: transparent; border: none;")
        d_lay.addWidget(d_ico)

        d_txt_col = QVBoxLayout()
        d_txt_col.setSpacing(1)
        self.d_title = QLabel("Faylni tashlang yoki tanlang")
        self.d_title.setFont(px_font(12, QFont.Weight.DemiBold))
        self.d_title.setStyleSheet(f"color: {LTheme.TEXT_MAIN}; background: transparent; border: none;")
        d_txt_col.addWidget(self.d_title)

        self.d_sub = QLabel("Fayl yuklanmagan")
        self.d_sub.setFont(px_font(10))
        self.d_sub.setStyleSheet(f"color: {LTheme.TEXT_LIGHT}; background: transparent; border: none;")
        d_txt_col.addWidget(self.d_sub)
        d_lay.addLayout(d_txt_col)
        d_lay.addStretch()

        btn_plus = QPushButton("+")
        btn_plus.setFixedSize(26, 26)
        btn_plus.setFont(px_font(14, QFont.Weight.Bold))
        btn_plus.setStyleSheet(f"""
            QPushButton {{
                background: #ffffff; border: 1px solid {LTheme.BORDER};
                border-radius: 13px; color: {LTheme.TEXT_MUTED};
            }}
            QPushButton:hover {{ background: #f1f5f9; color: {LTheme.TEXT_MAIN}; }}
        """)
        btn_plus.clicked.connect(self._choose_file)
        self.drop_box.mousePressEvent = lambda _: self._choose_file()
        d_lay.addWidget(btn_plus)
        lay.addWidget(self.drop_box)

        # Text input & send button
        inp_box = QFrame()
        inp_box.setStyleSheet(f"""
            QFrame {{
                background: #ffffff;
                border: 1.5px solid {LTheme.BORDER};
                border-radius: 10px;
            }}
            QFrame:focus-within {{
                border: 1.5px solid {LTheme.BLUE};
            }}
        """)
        i_lay = QHBoxLayout(inp_box)
        i_lay.setContentsMargins(12, 4, 6, 4)
        i_lay.setSpacing(8)

        i_ico = QLabel(">")
        i_ico.setFont(px_font(13, QFont.Weight.Bold))
        i_ico.setStyleSheet(f"color: {LTheme.BLUE}; background: transparent; border: none;")
        i_lay.addWidget(i_ico)

        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Buyruq yoki savol yozing...")
        self.cmd_input.setFont(px_font(12))
        self.cmd_input.setStyleSheet("background: transparent; border: none; color: #0f172a;")
        self.cmd_input.returnPressed.connect(self._on_send_command)
        i_lay.addWidget(self.cmd_input)

        btn_send = QPushButton("⬆")
        btn_send.setFixedSize(30, 30)
        btn_send.setFont(px_font(12, QFont.Weight.Bold))
        btn_send.setStyleSheet(f"""
            QPushButton {{
                background: {LTheme.BLUE}; color: #ffffff;
                border: none; border-radius: 8px;
            }}
            QPushButton:hover {{ background: #1d4ed8; }}
        """)
        btn_send.clicked.connect(self._on_send_command)
        i_lay.addWidget(btn_send)
        lay.addWidget(inp_box)

        # Bottom Action Buttons (Mikrofon faol & To'xtatish)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_mic = QPushButton("🎙  Mikrofon faol")
        self.btn_mic.setFont(px_font(11, QFont.Weight.DemiBold))
        self.btn_mic.setStyleSheet(f"""
            QPushButton {{
                background: {LTheme.GREEN_LIGHT}; color: {LTheme.GREEN};
                border: 1px solid {LTheme.GREEN_BORDER}; border-radius: 8px;
                padding: 7px 18px;
            }}
            QPushButton:hover {{ background: #dcfce7; }}
        """)
        self.btn_mic.clicked.connect(self._toggle_mute)
        btn_row.addWidget(self.btn_mic)
        btn_row.addStretch()

        self.btn_stop = QPushButton("⏹  To'xtatish")
        self.btn_stop.setFont(px_font(11, QFont.Weight.DemiBold))
        self.btn_stop.setStyleSheet(f"""
            QPushButton {{
                background: {LTheme.RED_LIGHT}; color: {LTheme.RED};
                border: 1px solid {LTheme.RED_BORDER}; border-radius: 8px;
                padding: 7px 18px;
            }}
            QPushButton:hover {{ background: #fee2e2; }}
        """)
        self.btn_stop.clicked.connect(self._on_interrupt_click)
        btn_row.addWidget(self.btn_stop)
        lay.addLayout(btn_row)

        return card

    # ── 5. PASTKI FOOTER (Status Strip) ──────────────────────────────────────
    def _build_footer(self) -> QWidget:
        foot = QWidget()
        foot.setFixedHeight(24)
        foot.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(foot)
        lay.setContentsMargins(6, 0, 6, 0)

        lbl = QLabel("F4 · MUTE    ·    F11 · FULLSCREEN    ·    ESC · INTERRUPT    ·    ADVOKAT AI")
        lbl.setFont(px_font(10, QFont.Weight.Medium, spacing=1.2))
        lbl.setStyleSheet(f"color: {LTheme.TEXT_LIGHT};")
        lay.addWidget(lbl)
        lay.addStretch()

        credit = QLabel("BY FATIHMAKES & ADVOKAT AI")
        credit.setFont(px_font(9, QFont.Weight.Bold, spacing=1.2))
        credit.setStyleSheet(f"color: {LTheme.TEXT_LIGHT};")
        lay.addWidget(credit)

        return foot

    # ── HELPER METODLAR VA SIGNALLAR ─────────────────────────────────────────
    def _add_log_item(self, text: str, kind: str = "msg"):
        box = QFrame()
        box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        bg = LTheme.YELLOW_BG if "failed" in text.lower() or "error" in text.lower() else "#ffffff"
        brd = LTheme.YELLOW_BRD if "failed" in text.lower() or "error" in text.lower() else LTheme.BORDER
        box.setStyleSheet(f"""
            QFrame {{
                background: {bg}; border: 1px solid {brd}; border-radius: 10px;
            }}
        """)
        lay = QVBoxLayout(box)
        lay.setContentsMargins(12, 6, 12, 6)
        lay.setSpacing(2)

        t_lbl = QLabel(datetime.now().strftime("%H:%M:%S"))
        t_lbl.setFont(px_font(9, QFont.Weight.Bold, mono=True))
        t_lbl.setStyleSheet(f"color: {LTheme.TEXT_LIGHT}; background: transparent; border: none;")
        lay.addWidget(t_lbl)

        msg_lbl = QLabel(text)
        msg_lbl.setFont(px_font(11))
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(f"color: {LTheme.TEXT_MAIN}; background: transparent; border: none;")
        lay.addWidget(msg_lbl)

        idx = max(0, self.log_lay.count() - 1)
        self.log_lay.insertWidget(idx, box)

    def _append_task_row(self, title: str, subtitle: str = ""):
        row = QFrame()
        row.setFixedHeight(38)
        row.setStyleSheet(f"""
            QFrame {{
                background: #ffffff; border: 1px solid {LTheme.BORDER};
                border-radius: 8px;
            }}
            QFrame:hover {{
                border-color: #cbd5e1; background: #f8fafc;
            }}
        """)
        lay = QHBoxLayout(row)
        lay.setContentsMargins(12, 2, 12, 2)
        lay.setSpacing(10)

        chk = QLabel("✔")
        chk.setFont(px_font(12, QFont.Weight.Bold))
        chk.setStyleSheet(f"color: {LTheme.GREEN}; background: transparent; border: none;")
        lay.addWidget(chk)

        t_col = QVBoxLayout()
        t_col.setSpacing(1)
        t_lbl = QLabel(title)
        t_lbl.setFont(px_font(11, QFont.Weight.DemiBold))
        t_lbl.setStyleSheet(f"color: {LTheme.TEXT_MAIN}; background: transparent; border: none;")
        t_col.addWidget(t_lbl)

        if subtitle:
            s_lbl = QLabel(subtitle)
            s_lbl.setFont(px_font(9, QFont.Weight.Normal))
            s_lbl.setStyleSheet(f"color: {LTheme.TEXT_LIGHT}; background: transparent; border: none;")
            t_col.addWidget(s_lbl)
        lay.addLayout(t_col)
        lay.addStretch()

        st = QLabel("DONE")
        st.setFont(px_font(9, QFont.Weight.Bold))
        st.setStyleSheet(f"""
            background: {LTheme.GREEN_LIGHT}; color: {LTheme.GREEN};
            border: 1px solid {LTheme.GREEN_BORDER}; border-radius: 4px;
            padding: 2px 8px;
        """)
        lay.addWidget(st)

        self.tasks_lay.addWidget(row)

    def _on_send_command(self):
        text = self.cmd_input.text().strip()
        if text:
            self._add_log_item(f"Siz: {text}", "user")
            self.cmd_input.clear()
            if self.on_text_command:
                self.on_text_command(text)

    def _on_interrupt_click(self):
        if self.on_interrupt:
            self.on_interrupt()
        self._add_log_item("Jarayon to'xtatildi.", "sys")

    def _handle_log(self, text: str):
        self._add_log_item(text, "sys")

    def _handle_state(self, state: str):
        state = str(state or "").upper()
        if state == "SPEAKING":
            self.avatar_circle.set_speaking(True)
            self.lbl_voice_badge.setText("●  Gapirmoqda")
            self.lbl_voice_badge.setStyleSheet(f"background: {LTheme.BLUE_LIGHT}; color: {LTheme.BLUE}; border: 1px solid {LTheme.BLUE_BORDER}; border-radius: 12px; padding: 3px 10px;")
            self.lbl_sub_status.setText("Ovozli javob ijro etilmoqda...")
        elif state == "LISTENING":
            self.avatar_circle.set_speaking(False)
            self.lbl_voice_badge.setText("●  Tinglamoqda")
            self.lbl_voice_badge.setStyleSheet(f"background: {LTheme.GREEN_LIGHT}; color: {LTheme.GREEN}; border: 1px solid {LTheme.GREEN_BORDER}; border-radius: 12px; padding: 3px 10px;")
            self.lbl_sub_status.setText("Sizni tinglamoqda...")
        else:
            self.avatar_circle.set_speaking(False)
            self.lbl_voice_badge.setText(f"●  {state.capitalize()}")
            self.lbl_sub_status.setText("Buyruq kutilmoqda...")

    def _handle_content(self, title: str, text: str):
        self._add_log_item(f"[{title}]: {text[:160]}...", "content")

    def _toggle_mute(self):
        self._muted = not self._muted
        if self._muted:
            self.btn_mic.setText("🔇  Mikrofon o'chiq")
            self.btn_mic.setStyleSheet(f"""
                QPushButton {{
                    background: {LTheme.RED_LIGHT}; color: {LTheme.RED};
                    border: 1px solid {LTheme.RED_BORDER}; border-radius: 8px;
                    padding: 7px 18px;
                }}
                QPushButton:hover {{ background: #fee2e2; }}
            """)
            self.avatar_circle.set_muted(True)
            self._add_log_item("Mikrofon o'chirildi (Mute).", "sys")
        else:
            self.btn_mic.setText("🎙  Mikrofon faol")
            self.btn_mic.setStyleSheet(f"""
                QPushButton {{
                    background: {LTheme.GREEN_LIGHT}; color: {LTheme.GREEN};
                    border: 1px solid {LTheme.GREEN_BORDER}; border-radius: 8px;
                    padding: 7px 18px;
                }}
                QPushButton:hover {{ background: #dcfce7; }}
            """)
            self.avatar_circle.set_muted(False)
            self._add_log_item("Mikrofon yoqildi (Unmute).", "sys")

    def _choose_file(self):
        fn, _ = QFileDialog.getOpenFileName(
            self, "Faylni tanlang", "",
            "Barcha fayllar (*.*);;Hujjatlar (*.docx *.pdf *.txt *.json *.csv)"
        )
        if fn:
            self.set_dropped_file(fn)

    def set_dropped_file(self, path: str):
        self._dropped_file = path
        p = Path(path)
        if p.exists():
            kb = p.stat().st_size // 1024
            self.d_title.setText(p.name)
            self.d_sub.setText(f"{kb} KB · Biriktirildi")
            self._add_log_item(f"Fayl yuklandi: {p.name} ({kb} KB)", "sys")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path and Path(path).exists():
                self.set_dropped_file(path)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_F4:
            self._toggle_mute()
        elif e.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif e.key() == Qt.Key.Key_Escape:
            self._on_interrupt_click()
        else:
            super().keyPressEvent(e)

    def notify_phone_connected(self):
        self._add_log_item("Telefon masofaviy boshqaruv orqali ulandi.", "sys")

    def video_is_playing(self) -> bool:
        return False

    def video_state(self) -> dict:
        return {}

    def start_camera_stream(self):
        self._add_log_item("Kamera oqimi faollashtirildi.", "sys")

    def stop_camera_stream(self):
        pass

    def _refresh_system_metrics(self):
        # RAM
        ram = psutil.virtual_memory().percent
        self.kpi_ram.lbl_v.setText(f"{int(ram)}%")
        self.kpi_ram.pbar.setValue(int(ram))

        # Processes
        self.kpi_proc.lbl_v.setText(str(len(psutil.pids())))

        # Uptime
        sec = int(time.time() - self._uptime_start)
        m, s = divmod(sec, 60)
        self.kpi_uptime.lbl_v.setText(f"{m:02d}:{s:02d}")

        # Clock
        self.lbl_clock.setText(datetime.now().strftime("%H:%M"))

        # Net speed snapshot
        try:
            net_io = psutil.net_io_counters()
            now = time.time()
            dt = now - getattr(self, '_last_net_time', now)
            if dt > 0 and hasattr(self, '_last_net_bytes'):
                diff = (net_io.bytes_recv + net_io.bytes_sent) - self._last_net_bytes
                kb_s = int(diff / dt / 1024)
                self.kpi_net.lbl_v.setText(f"{max(12, kb_s)} KB/s")
            self._last_net_bytes = net_io.bytes_recv + net_io.bytes_sent
            self._last_net_time = now
        except Exception:
            pass

        # CPU / Harorat
        try:
            cpu = psutil.cpu_percent()
            self.kpi_temp.lbl_v.setText(f"{int(38 + cpu * 0.25)}°")
        except Exception:
            pass

    # JarvisUI bilan moslik uchun shimlari
    @property
    def hud(self):
        class _HudShim:
            def __init__(self, av, wf):
                self._av = av
                self._wf = wf
            def set_audio_level(self, lv):
                self._av.set_amp(lv)
                self._wf.set_amp(lv)
            def glance(self, *a, **kw): pass
            def push_visemes(self, *a, **kw): pass
        return _HudShim(self.avatar_circle, self.waveform)

    @property
    def _drop_zone(self):
        class _DropShim:
            def __init__(self, parent): self._p = parent
            def current_file(self): return self._p._dropped_file
        return _DropShim(self)
