#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
دليل إعداد وتشغيل نظام SMILE CAFE POS
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_requirements():
    """فحص المتطلبات الأساسية"""
    print("🔍 فحص المتطلبات...")
    
    # فحص Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print("❌ يتطلب Python 3.7 أو أحدث")
        return False
    else:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # فحص المكتبات
    required_packages = ['flask', 'flask_sqlalchemy', 'qrcode', 'pillow']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} مثبت")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} غير مثبت")
    
    if missing_packages:
        print(f"\n📦 تثبيت المكتبات الناقصة:")
        install_cmd = f"pip install {' '.join(missing_packages)}"
        print(f"   {install_cmd}")
        
        # محاولة التثبيت التلقائي
        try:
            subprocess.run(install_cmd, check=True, shell=True)
            print("✅ تم تثبيت المكتبات بنجاح")
        except subprocess.CalledProcessError:
            print("❌ فشل التثبيت. قم بتشغيل الأمر يدوياً:")
            print(f"   {install_cmd}")
            return False
    
    return True

def setup_network():
    """إعداد الشبكة للوصول من الأجهزة الأخرى"""
    print("\n🌐 إعداد الشبكة...")
    
    import socket
    
    # الحصول على IP المحلي
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        print(f"✅ IP المحلي: {local_ip}")
        print(f"📱 رابط الهاتف: http://{local_ip}:5000")
        print(f"📱 QR Code: http://{local_ip}:5000/qr.html")
        print(f"📱 القائمة: http://{local_ip}:5000/menu.html")
        
        return local_ip
    except Exception as e:
        print(f"❌ خطأ في الحصول على IP: {e}")
        return "localhost"

def create_desktop_shortcut():
    """إنشاء اختصار على سطح المكتب"""
    print("\n🖥️ إنشاء اختصار على سطح المكتب...")
    
    import os
    import json
    
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.exists(desktop):
        desktop = os.path.expanduser("~")
    
    shortcut_path = os.path.join(desktop, "SMILE_CAFE_POS.bat")
    
    # إنشاء ملف دفعي
    with open(shortcut_path, 'w', encoding='utf-8') as f:
        f.write('''@echo off
echo 🚀 تشغيل نظام SMILE CAFE POS...
echo.
cd /d "%~dp0"
python app.py
pause
''')
    
    print(f"✅ تم إنشاء اختصار: {shortcut_path}")
    return shortcut_path

def start_server():
    """تشغيل الخادم"""
    print("\n🚀 تشغيل الخادم...")
    
    try:
        # تشغيل تطبيق Flask
        os.system("python app.py")
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف الخادم")
    except Exception as e:
        print(f"❌ خطأ في تشغيل الخادم: {e}")

def main():
    """الدالة الرئيسية"""
    print("=" * 60)
    print("🍽️  SMILE CAFE POS - دليل الإعداد والتشغيل")
    print("=" * 60)
    
    # فحص المتطلبات
    if not check_requirements():
        print("\n❌ يرجى تثبيت المتطلبات أولاً")
        return
    
    # إعداد الشبكة
    local_ip = setup_network()
    
    # إنشاء اختصار
    create_desktop_shortcut()
    
    print("\n" + "=" * 60)
    print("📋 روابط النظام:")
    print("=" * 60)
    print(f"🖥️  اللابتوب: http://localhost:5000")
    print(f"📱 الهاتف: http://{local_ip}:5000")
    print(f"🍽️  القائمة: http://{local_ip}:5000/menu.html")
    print(f"📱 QR Code: http://{local_ip}:5000/qr.html")
    print(f"⚙️  لوحة التحكم: http://{local_ip}:5000/admin")
    print("=" * 60)
    
    print("\n🚀 جاري تشغيل الخادم...")
    print("💡 لإيقاف الخادم: اضغط Ctrl+C")
    
    # تشغيل الخادم
    start_server()

if __name__ == "__main__":
    main()
