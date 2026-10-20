@echo off
chcp 65001 > nul
echo ======================================================================
echo 🏛️ ADVOKAT AI (MARK 57) — WINDOWS DASTURIY PAKETINI YARATISH (BUILD)
echo ======================================================================
echo.

if not exist "dist" mkdir dist
if not exist "build" mkdir build

echo [1/3] Fayllar tekshirilmoqda va muhit sozlanmoqda...
python -c "import PyInstaller, PyQt6, docx; print('✅ Barcha kutubxonalar mavjud!')"
if %errorlevel% neq 0 (
    echo ❌ Xatolik: PyInstaller yoki PyQt6 topilmadi!
    pause
    exit /b %errorlevel%
)

echo.
echo [2/3] PyInstaller orqali Windows .EXE paketi yig'ilmoqda...
echo (Bu jarayon bir necha daqiqa vaqt olishi mumkin, iltimos kuting...)
python -m PyInstaller --noconfirm AdvokatAI.spec

if %errorlevel% neq 0 (
    echo.
    echo ❌ Kompilyatsiyada xatolik yuz berdi!
    pause
    exit /b %errorlevel%
)

echo.
echo [3/3] Windows o'rnatish paketi tayyor!
echo Chiqish yo'li: dist\AdvokatAI_Mark57\AdvokatAI_Mark57.exe
echo.
echo ======================================================================
echo 🎉 TAYYOR! ADVOKAT AI DASTURI WINDOWS UCHUN TO'LIQ PAKETLANDI!
echo ======================================================================
pause
