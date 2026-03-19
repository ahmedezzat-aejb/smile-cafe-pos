#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إضافة مسار QR Code الدينامي لتطبيق Flask
"""

from flask import send_file
import io
import base64
from generate_qr import generate_real_qr

def add_qr_routes(app):
    """إضافة مسارات QR Code إلى تطبيق Flask"""
    
    @app.route('/qr/generate')
    def generate_qr_api():
        """API لإنشاء QR Code ديناميكي"""
        qr_base64 = generate_real_qr()
        return jsonify({'qr_code': qr_base64})
    
    @app.route('/qr/image')
    def qr_image():
        """خدمة صورة QR Code"""
        try:
            return send_file('smile_cafe_qr_real.png', mimetype='image/png')
        except FileNotFoundError:
            # إذا لم تكن الصورة موجودة، قم بإنشائها
            generate_real_qr()
            return send_file('smile_cafe_qr_real.png', mimetype='image/png')

if __name__ == "__main__":
    print("استخدم هذا الملف مع تطبيق Flask الرئيسي")
