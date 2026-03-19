#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مولد QR Code حقيقي لـ SMILE CAFE
"""

import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import base64

def generate_real_qr():
    """إنشاء QR Code حقيقي يحتوي على رابط القائمة مباشرة"""
    
    # رابط القائمة المباشر
    menu_url = 'http://localhost:5000/menu.html'
    
    # إنشاء QR Code مع الرابط فقط للنقل المباشر
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    qr.add_data(menu_url)
    qr.make(fit=True)
    
    # إنشاء صورة QR Code
    qr_img = qr.make_image(fill_color="#6f4e37", back_color="white")
    
    # إضافة شعار المقهى في المنتصف
    logo_size = 60
    logo = Image.new('RGBA', (logo_size, logo_size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(logo)
    
    # رسم شعار بسيط (قهوة)
    draw.ellipse([10, 15, 50, 55], fill="#6f4e37")
    draw.rectangle([20, 25, 40, 35], fill="white")
    draw.text([25, 28], "☕", fill="#6f4e37", font_size=20)
    
    # وضع الشعار في منتصف QR Code
    pos = ((qr_img.size[0] - logo_size) // 2, (qr_img.size[1] - logo_size) // 2)
    qr_img.paste(logo, pos, logo)
    
    # حفظ الصورة
    qr_img.save('smile_cafe_qr_real.png')
    
    # تحويل إلى base64 للعرض في HTML
    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return img_base64

def generate_menu_qr():
    """إنشاء QR Code لصفحة القائمة فقط"""
    
    menu_url = 'http://localhost:5000/menu.html'
    
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    
    qr.add_data(menu_url)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="#27ae60", back_color="white")
    qr_img.save('menu_qr.png')
    
    # تحويل إلى base64
    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return img_base64

if __name__ == "__main__":
    print("🔄 جاري إنشاء QR Code حقيقي...")
    
    # إنشاء QR Code الرئيسي
    main_qr = generate_real_qr()
    
    # إنشاء QR Code للقائمة
    menu_qr = generate_menu_qr()
    
    print("✅ تم إنشاء QR Code بنجاح!")
    print("📱 يمكنك مسح الكود الآن للحصول على معلومات المقهى")
    print("🍽️ أو استخدام QR Code القائمة للوصول المباشر للمنيو")
