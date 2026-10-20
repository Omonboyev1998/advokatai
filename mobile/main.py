"""
mobile/main.py — ADVOKAT AI Native Kivy Android App Entrypoint.
Buildozer va Python-for-Android orqali haqiqiy .apk formatida kompilyatsiya qilinadi.
"""
import os
import sys

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

# Cyber dark background
Window.clearcolor = get_color_from_hex("#000a12")


class AdvokatMobileLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=10, padding=15, **kwargs)

        # 1. Header
        header = BoxLayout(orientation="horizontal", size_hint_y=0.12, spacing=10)
        icon = Image(source="face.png", size_hint_x=0.25)
        title = Label(
            text="[b][color=00e5ff]ADVOKAT AI[/color][/b]\n[size=12]Mark 57 · Mobil Versiya[/size]",
            markup=True,
            font_size="16sp",
            size_hint_x=0.75,
            halign="left",
            valign="middle"
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(icon)
        header.add_widget(title)
        self.add_widget(header)

        # 2. Status Card
        status = Label(
            text="[color=00e676]● FAOLLASHTIRILGAN[/color] · 14 kunlik sinov muddati\n[size=11][color=78909c]Yuridik sun'iy intellekt xizmatingizda[/size][/color]",
            markup=True,
            font_size="13sp",
            size_hint_y=0.10,
            halign="center"
        )
        self.add_widget(status)

        # 3. Chat / Result Scroll Area
        self.output_label = Label(
            text=(
                "Assalomu alaykum!\n"
                "Men — Advokat AI, O'zbekiston Respublikasi Huquqiy Sun'iy Intellekti.\n\n"
                "Quyidagi xizmatlardan foydalanishingiz mumkin:\n"
                "• 📜 my.sud.uz da'vo arizalari yaratish\n"
                "• 🔍 Shartnomalar auditi va xatarlar\n"
                "• 🧮 Davlat boji va penya hisoblash"
            ),
            markup=True,
            font_size="13sp",
            size_hint_y=None,
            color=get_color_from_hex("#e0f7fa"),
            halign="left",
            valign="top"
        )
        self.output_label.bind(width=lambda *x: setattr(self.output_label, 'text_size', (self.output_label.width, None)))
        self.output_label.bind(texture_size=lambda *x: setattr(self.output_label, 'height', self.output_label.texture_size[1]))

        scroll = ScrollView(size_hint_y=0.45)
        scroll.add_widget(self.output_label)
        self.add_widget(scroll)

        # 4. Action Buttons Grid
        btn_grid = BoxLayout(orientation="horizontal", size_hint_y=0.12, spacing=8)
        
        btn_draft = Button(
            text="📜 Da'vo",
            background_normal="",
            background_color=get_color_from_hex("#002235"),
            color=get_color_from_hex("#00e5ff"),
            bold=True
        )
        btn_draft.bind(on_press=self.on_draft)

        btn_audit = Button(
            text="🔍 Audit",
            background_normal="",
            background_color=get_color_from_hex("#002235"),
            color=get_color_from_hex("#00e5ff"),
            bold=True
        )
        btn_audit.bind(on_press=self.on_audit)

        btn_calc = Button(
            text="🧮 Boj",
            background_normal="",
            background_color=get_color_from_hex("#002235"),
            color=get_color_from_hex("#00e5ff"),
            bold=True
        )
        btn_calc.bind(on_press=self.on_calc)

        btn_grid.add_widget(btn_draft)
        btn_grid.add_widget(btn_audit)
        btn_grid.add_widget(btn_calc)
        self.add_widget(btn_grid)

        # 5. Input & Send
        input_box = BoxLayout(orientation="horizontal", size_hint_y=0.11, spacing=8)
        self.text_input = TextInput(
            hint_text="Savolingizni yozing...",
            multiline=False,
            background_color=get_color_from_hex("#00121d"),
            foreground_color=get_color_from_hex("#ffffff"),
            cursor_color=get_color_from_hex("#00e5ff"),
            size_hint_x=0.78
        )
        btn_send = Button(
            text="➔",
            size_hint_x=0.22,
            background_normal="",
            background_color=get_color_from_hex("#00e5ff"),
            color=get_color_from_hex("#000c14"),
            bold=True,
            font_size="18sp"
        )
        btn_send.bind(on_press=self.on_send)
        input_box.add_widget(self.text_input)
        input_box.add_widget(btn_send)
        self.add_widget(input_box)

    def on_send(self, instance):
        q = self.text_input.text.strip()
        if not q:
            return
        self.output_label.text += f"\n\n[b][color=00e5ff]Siz:[/color][/b] {q}\n[b][color=00e676]Advokat AI:[/color][/b] Savolingiz qabul qilindi. O'zbekiston Respublikasi Fuqarolik Kodeksi talablari asosida tahlil qilinmoqda..."
        self.text_input.text = ""

    def on_draft(self, instance):
        self.output_label.text += "\n\n[b][color=00e5ff]Advokat AI:[/color][/b] Qarz undirish bo'yicha da'vo arizasi shabloni tayyorlandi:\nFUQAROLIK ISHLARI BO'YICHA SUDGA\nDa'vogar: Karimov A.\nJavobgar: Toshmatov B.\nDa'vo bahosi: 10 000 000 so'm\nDavlat boji: 400 000 so'm (4%)\n\nFK 732, 735-moddalariga asosan qarz summasini undirishni so'rayman."

    def on_audit(self, instance):
        self.output_label.text += "\n\n[b][color=00e5ff]Advokat AI (Audit):[/color][/b] Shartnomada noqulay bandlar aniqlandi:\n⚠️ Kunlik 5% jarima bekor qilinishi lozim (qonuniy limit 0.5%).\n💡 Tavsiya: Jarimani 0.1% ga o'zgartiring."

    def on_calc(self, instance):
        self.output_label.text += "\n\n[b][color=00e5ff]Advokat AI (Kalkulyator):[/color][/b]\nDavlat boji stavkalari (BHM = 375 000 so'm):\n• Mulkiy da'volar: da'vo bahosining 4% (kamida 1 BHM)\n• Nomulkiy da'volar: 2 BHM (750 000 so'm)\n• Nikohni bekor qilish: 2 BHM (750 000 so'm)"


class AdvokatApp(App):
    title = "Advokat AI"
    icon = "face.png"

    def build(self):
        return AdvokatMobileLayout()


if __name__ == "__main__":
    AdvokatApp().run()
