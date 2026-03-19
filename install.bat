@echo off
echo 🌟 تثبيت SMILE CAFE POS - الإصدار المتقدم
echo =====================================
echo.

echo 📦 تثبيت المكتبات المطلوبة...
pip install qrcode[pil] pillow
pip install flask flask-sqlalchemy

echo.
echo ✅ تم التثبيت بنجاح!
echo.
echo 🚀 تشغيل الخادم...
python server.py

pause
