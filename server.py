#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.server
import socketserver
import os
import webbrowser
import json
import sqlite3
from datetime import datetime
from threading import Timer
import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# تعيين المجلد الحالي
PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_GET(self):
        if self.path == '/api/menu':
            self.serve_menu_api()
        elif self.path == '/api/qrcode':
            self.serve_qr_code()
        elif self.path == '/api/prices':
            self.serve_prices_api()
        else:
            super().do_GET()
    
    def serve_menu_api(self):
        """تقديم قائمة المنتجات كـ API"""
        menu = {
            "sections": {
                "☕ مشروبات ساخنة": [
                    {"name": "قهوة تركي", "price": 35, "icon": "☕"},
                    {"name": "قهوة تركي محوج", "price": 40, "icon": "☕"},
                    {"name": "قهوة باللبن", "price": 50, "icon": "☕"},
                    {"name": "نسكافيه (بلاك)", "price": 40, "icon": "☕"},
                    {"name": "نسكافيه (جولد)", "price": 45, "icon": "☕"},
                    {"name": "كابتشينو (S)", "price": 60, "icon": "☕"},
                    {"name": "كابتشينو (L)", "price": 70, "icon": "☕"},
                    {"name": "لاتيه", "price": 65, "icon": "☕"},
                    {"name": "هوت شوكلت", "price": 65, "icon": "🔥"},
                    {"name": "شاي سادة", "price": 20, "icon": "🍵"},
                    {"name": "شاي فتلة", "price": 25, "icon": "🍵"},
                    {"name": "شاي أخضر", "price": 25, "icon": "🍵"}
                ],
                "🧊 مشروبات مثلجة": [
                    {"name": "آيس كوفي", "price": 65, "icon": "🧊"},
                    {"name": "آيس لاتيه", "price": 70, "icon": "🧊"},
                    {"name": "آيس موكا", "price": 75, "icon": "🧊"},
                    {"name": "فرابيه أوريو", "price": 75, "icon": "🥤"},
                    {"name": "فرابيه كراميل", "price": 75, "icon": "🥤"},
                    {"name": "سموزي مانجو", "price": 60, "icon": "🥤"},
                    {"name": "سموزي فراولة", "price": 60, "icon": "🥤"},
                    {"name": "سموزي خوخ", "price": 60, "icon": "🥤"},
                    {"name": "ميلك شيك فانيليا", "price": 70, "icon": "🥛"},
                    {"name": "ميلك شيك شوكولاتة", "price": 70, "icon": "🥛"},
                    {"name": "ميلك شيك مانجو", "price": 70, "icon": "🥛"}
                ],
                "🍽️ وجبات": [
                    {"name": "وجبة أولى (ربع فرخة)", "price": 180, "icon": "🍗"},
                    {"name": "وجبة ثانية (2 برجر)", "price": 190, "icon": "🍔"},
                    {"name": "وجبة ثالثة (نصف فرخة)", "price": 240, "icon": "🍗"},
                    {"name": "وجبة رابعة (كفتة+فرخة)", "price": 210, "icon": "🍽️"}
                ],
                "🍕 بيتزا وكريب": [
                    {"name": "بيتزا مارجريتا (M)", "price": 120, "icon": "🍕"},
                    {"name": "بيتزا مارجريتا (L)", "price": 140, "icon": "🍕"},
                    {"name": "بيتزا مشكل جبن (M)", "price": 140, "icon": "🍕"},
                    {"name": "بيتزا فراخ (M)", "price": 160, "icon": "🍕"},
                    {"name": "كريب نوتيلا (S)", "price": 60, "icon": "🥞"},
                    {"name": "كريب نوتيلا (L)", "price": 80, "icon": "🥞"},
                    {"name": "كريب فراخ بانيه (S)", "price": 110, "icon": "🥞"},
                    {"name": "كريب فراخ بانيه (L)", "price": 130, "icon": "🥞"}
                ],
                "🥪 سندوتشات": [
                    {"name": "برجر سادة", "price": 80, "icon": "🍔"},
                    {"name": "برجر جبنة", "price": 95, "icon": "🍔"},
                    {"name": "فراخ بانيه", "price": 90, "icon": "🍗"},
                    {"name": "هوت دوج", "price": 75, "icon": "🌭"},
                    {"name": "بطاطس سوري", "price": 50, "icon": "🍟"}
                ],
                "💨 شيشة": [
                    {"name": "حجر فاخر تفاح", "price": 90, "icon": "💨"},
                    {"name": "حجر فاخر خوخ", "price": 90, "icon": "💨"},
                    {"name": "حجر فاخر كريز", "price": 90, "icon": "💨"},
                    {"name": "حجر فاخر عنب", "price": 90, "icon": "💨"},
                    {"name": "حجر فاخر فراولة", "price": 90, "icon": "💨"},
                    {"name": "حجر فاخر مانجو", "price": 90, "icon": "💨"},
                    {"name": "حجر فاخر جوافة", "price": 90, "icon": "💨"},
                    {"name": "حجر فاخر برتقال", "price": 90, "icon": "💨"},
                    {"name": "حجر فاخر ليمون", "price": 90, "icon": "💨"},
                    {"name": "حجر فاخر نعناع", "price": 90, "icon": "💨"},
                    {"name": "حجر فاخر كركديه", "price": 90, "icon": "💨"},
                    {"name": "حجر ميكس VIP", "price": 100, "icon": "💨"},
                    {"name": "حجر ميكس عادي", "price": 80, "icon": "💨"}
                ],
                "🍦 حلويات": [
                    {"name": "فخفخينا (S)", "price": 70, "icon": "🍞"},
                    {"name": "زبادي خلاط سادة", "price": 40, "icon": "🍦"},
                    {"name": "زبادي خلاط فواكه", "price": 45, "icon": "🍦"},
                    {"name": "قنبلة سمايل", "price": 50, "icon": "💣"},
                    {"name": "ميكس نوتيلا", "price": 55, "icon": "🍦"}
                ],
                "➕ خدمات": [
                    {"name": "إضافة لي طبي", "price": 20, "icon": "➕"},
                    {"name": "إضافة جبنة", "price": 25, "icon": "➕"},
                    {"name": "إضافة لحوم", "price": 40, "icon": "➕"}
                ]
            },
            "last_updated": datetime.now().isoformat(),
            "restaurant_name": "SMILE CAFE",
            "service_charge": 0.12
        }
        
        self.send_response(200, 'application/json', json.dumps(menu, ensure_ascii=False, indent=2))
    
    def serve_qr_code(self):
        """إنشاء وتقديم QR Code للقائمة"""
        try:
            # إنشاء QR Code مع رابط القائمة
            menu_url = f"http://localhost:{PORT}/menu.html"
            
            # إنشاء QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(menu_url)
            qr.make(fit=True)
            
            # تحويل إلى صورة
            img = qr.make_image(fill_color="#6f4e37", back_color="white")
            
            # إضافة عنوان للصورة
            img_with_text = Image.new('RGB', (img.width, img.height + 60), 'white')
            img_with_text.paste(img, (0, 0))
            
            draw = ImageDraw.Draw(img_with_text)
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # إضافة النص
            text = "SMILE CAFE - قائمة الطعام"
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (img_with_text.width - text_width) // 2
            draw.text((text_x, img.height + 20), text, fill="#6f4e37", font=font)
            
            # تحويل إلى bytes
            img_bytes = io.BytesIO()
            img_with_text.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # تحويل إلى base64
            img_base64 = base64.b64encode(img_bytes.getvalue()).decode()
            
            # إنشاء HTML page للـ QR Code
            qr_html = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>SMILE CAFE - QR Code</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #f5e6d3, #e8d5b7);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 20px;
        }}
        .qr-container {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(111, 78, 55, 0.3);
            text-align: center;
            max-width: 400px;
        }}
        .qr-title {{
            color: #6f4e37;
            font-size: 2rem;
            margin-bottom: 20px;
            font-weight: bold;
        }}
        .qr-subtitle {{
            color: #8b5a3c;
            font-size: 1.2rem;
            margin-bottom: 30px;
        }}
        .qr-image {{
            margin: 20px 0;
            border: 3px solid #6f4e37;
            border-radius: 10px;
            padding: 10px;
            background: white;
        }}
        .qr-image img {{
            max-width: 100%;
            height: auto;
        }}
        .qr-instructions {{
            color: #6f4e37;
            font-size: 1rem;
            margin-top: 20px;
            line-height: 1.6;
        }}
        .btn {{
            background: #6f4e37;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1rem;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s ease;
        }}
        .btn:hover {{
            background: #8b5a3c;
            transform: translateY(-2px);
        }}
        .download-btn {{
            background: #27ae60;
        }}
        .download-btn:hover {{
            background: #229954;
        }}
    </style>
</head>
<body>
    <div class="qr-container">
        <div class="qr-title">☕ SMILE CAFE</div>
        <div class="qr-subtitle">قائمة الطعام الرقمية</div>
        
        <div class="qr-image">
            <img src="data:image/png;base64,{img_base64}" alt="QR Code للقائمة">
        </div>
        
        <div class="qr-instructions">
            <strong>كيفية الاستخدام:</strong><br>
            1. افتح كاميرا الهاتف<br>
            2. امسح الكود<br>
            3. استعرض القائمة الكاملة<br>
            4. اطلب مباشرة من هاتفك
        </div>
        
        <button class="btn download-btn" onclick="downloadQR()">
            📥 تحميل QR Code
        </button>
        
        <button class="btn" onclick="window.print()">
            🖨️ طباعة
        </button>
    </div>
    
    <script>
        function downloadQR() {{
            const link = document.createElement('a');
            link.download = 'smile-cafe-qr.png';
            link.href = document.querySelector('.qr-image img').src;
            link.click();
        }}
        
        // تحديث تلقائي كل 5 دقائق
        setInterval(() => {{
            window.location.reload();
        }}, 300000);
    </script>
</body>
</html>
            """
            
            self.send_response(200, 'text/html; charset=utf-8', qr_html)
            
        except Exception as e:
            self.send_response(500, 'text/plain', f'Error generating QR code: {str(e)}')
    
    def serve_prices_api(self):
        """تقديم الأسعار الحالية كـ API"""
        prices = {
            "last_updated": datetime.now().isoformat(),
            "currency": "ج.م",
            "service_charge": 0.12,
            "update_frequency": "auto"
        }
        
        self.send_response(200, 'application/json', json.dumps(prices, ensure_ascii=False, indent=2))
    
    def send_response(self, code, content_type, content):
        self.send_response_only()
        self.send_header('Content-type', content_type)
        self.send_header('Content-Length', str(len(content.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

def create_menu_page():
    """إنشاء صفحة القائمة للعملاء"""
    menu_html = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SMILE CAFE - قائمة الطعام</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #f5e6d3, #e8d5b7);
            min-height: 100vh;
            direction: rtl;
            padding: 20px;
        }
        
        .header {
            background: #6f4e37;
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        .section h2 {
            color: #6f4e37;
            font-size: 1.5rem;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .products {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .product {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .product:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
            border-color: #6f4e37;
        }
        
        .product-icon {
            font-size: 1.5rem;
            margin-bottom: 8px;
        }
        
        .product-name {
            font-weight: bold;
            margin-bottom: 8px;
            color: #333;
            font-size: 0.9rem;
        }
        
        .product-price {
            font-size: 1.1rem;
            color: #6f4e37;
            font-weight: bold;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #6f4e37;
            margin-top: 30px;
        }
        
        .last-updated {
            background: rgba(111, 78, 55, 0.1);
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-size: 0.9rem;
        }
        
        .auto-update {
            background: #27ae60;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .products {
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            }
            
            .header h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>☕ SMILE CAFE</h1>
        <p>قائمة الطعام الرقمية</p>
    </div>

    <div class="container">
        <div id="menu-content">
            <!-- سيتم تحميل القائمة هنا -->
        </div>
        
        <div class="footer">
            <p>🌟 SMILE CAFE - قائمة الطعام الرقمية</p>
            <div class="last-updated" id="last-updated">
                جاري تحميل القائمة...
            </div>
            <div class="auto-update">
                🔄 تحديث تلقائي للأسعار
            </div>
        </div>
    </div>

    <script>
        let menuData = null;
        
        // تحميل القائمة
        async function loadMenu() {
            try {
                const response = await fetch('/api/menu');
                menuData = await response.json();
                renderMenu();
                updateLastUpdated();
            } catch (error) {
                console.error('Error loading menu:', error);
                document.getElementById('menu-content').innerHTML = 
                    '<div class="section"><h2>خطأ في تحميل القائمة</h2></div>';
            }
        }
        
        // عرض القائمة
        function renderMenu() {
            const container = document.getElementById('menu-content');
            let html = '';
            
            for (const [sectionName, products] of Object.entries(menuData.sections)) {
                html += `
                    <div class="section">
                        <h2>${sectionName}</h2>
                        <div class="products">
                `;
                
                products.forEach(product => {
                    html += `
                        <div class="product">
                            <div class="product-icon">${product.icon}</div>
                            <div class="product-name">${product.name}</div>
                            <div class="product-price">${product.price.toFixed(2)} ج.م</div>
                        </div>
                    `;
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        }
        
        // تحديث وقت آخر تحديث
        function updateLastUpdated() {
            if (menuData && menuData.last_updated) {
                const date = new Date(menuData.last_updated);
                const formatted = date.toLocaleString('ar-EG', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                document.getElementById('last-updated').innerHTML = 
                    `📅 آخر تحديث: ${formatted}`;
            }
        }
        
        // تحديث تلقائي كل 5 دقائق
        setInterval(() => {
            loadMenu();
        }, 300000);
        
        // تحميل القائمة عند بدء الصفحة
        loadMenu();
    </script>
</body>
</html>
    """
    
    with open(os.path.join(DIRECTORY, 'menu.html'), 'w', encoding='utf-8') as f:
        f.write(menu_html)

def open_browser():
    """فتح المتصفح تلقائياً"""
    urls = [
        f'http://localhost:{PORT}/index.html',
        f'http://localhost:{PORT}/admin.html',
        f'http://localhost:{PORT}/qr.html'
    ]
    
    for url in urls:
        try:
            webbrowser.open(url)
            break
        except:
            continue

def start_server():
    """بدء الخادم"""
    # إنشاء صفحة القائمة
    create_menu_page()
    
    handler = CustomHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                      🌟 SMILE CAFE POS SERVER - الإصدار المتقدم 🌟                   ║
╠════════════════════════════════════════════════════════════════════════════════════╣
║  📍 الخادم يعمل الآن على:                                                    ║
║     http://localhost:{PORT}                                                  ║
║     http://127.0.0.1:{PORT}                                                 ║
║                                                                              ║
║  🔗 الروابط المباشرة:                                                          ║
║     • نقطة البيع:    http://localhost:{PORT}/index.html                  ║
║     • لوحة التحكم:   http://localhost:{PORT}/admin.html                  ║
║     • قائمة العملاء: http://localhost:{PORT}/menu.html                   ║
║     • QR Code:       http://localhost:{PORT}/qr.html                      ║
║                                                                              ║
║  📱 للوصول من الأجهزة الأخرى:                                              ║
║     • استخدم IP الجهاز: http://[YOUR_IP]:{PORT}                           ║
║     • أو امسح QR Code للوصول السريع                                       ║
║                                                                              ║
║  🎨 المميزات المتقدمة:                                                        ║
║     • قائمة رقمية للعملاء                                                   ║
║     • QR Code تلقائي                                                        ║
║     • تحديث تلقائي للأسعار                                                 ║
║     • وصول من اللاب توب والهاتف                                          ║
║     • لوحة تحكم للمدير                                                    ║
║                                                                              ║
║  🔄 تحديث تلقائي كل 5 دقائق                                               ║
║  ⚡ اضغط Ctrl+C لإيقاف الخادم                                            ║
╚════════════════════════════════════════════════════════════════════════════════════╝
        """)
        
        # فتح المتصفح بعد ثانيتين
        Timer(2.0, open_browser)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 تم إيقاف الخادم بنجاح")

if __name__ == "__main__":
    start_server()
