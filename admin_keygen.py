"""
admin_keygen.py — ADVOKAT AI Mustaqil Litsenziya Kalit Generatori va Muddat Boshqaruvi.
Administrator / Sotuvchi ushbu dasturni to'g'ridan-to'g'ri ishga tushirib,
mijozlarga istalgan muddatga (15 kun, 1 oy, 3 oy, 6 oy, 1 yil, cheksiz)
kriptografik litsenziya kalitlarini yaratishi mumkin.
"""
import sys
from pathlib import Path

# Loyiha ildiz papkasini sys.path ga qo'shish
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

from gui.theme import C
from gui.overlays import LicenseOverlay


class AdminKeygenWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚖️ ADVOKAT AI — Administrator Litsenziya Kalit Generatori")
        self.setStyleSheet(f"background: {C.BG};")
        
        icon_path = ROOT / "face.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self._overlay = LicenseOverlay()
        # Admin tabini birdan ochish va avtomatik qulfdan chiqarish
        self._overlay._switch_tab(1)
        self._overlay._admin_unlocked = True
        self._overlay._pin_container.hide()
        self._overlay._gen_panel.show()
        self._overlay._admin_fill_current_pc()

        self.setCentralWidget(self._overlay)
        self.setFixedSize(self._overlay.width(), self._overlay.height())


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = AdminKeygenWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
