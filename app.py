from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==========================================
# 1. جداول قاعدة البيانات (Database Models)
# ==========================================

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(10), nullable=True)
    price = db.Column(db.Float, nullable=False)
    recipe = db.Column(db.String(500), nullable=True)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False, unique=True)
    quantity = db.Column(db.Float, nullable=False, default=0)
    unit = db.Column(db.String(20), nullable=False)
    low_stock_threshold = db.Column(db.Float, default=100)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_num = db.Column(db.String(20), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    final_total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Open')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    waiter_id = db.Column(db.Integer, nullable=True)
    items = db.Column(db.String(1000), nullable=False)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    shift = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=True)

# ==========================================
# 2. منطق المخزون والعمليات (Inventory Logic)
# ==========================================

def deduct_inventory(product_id, quantity=1):
    product = Product.query.get(product_id)
    if product and product.recipe:
        recipe = json.loads(product.recipe)
        for item_name, item_deduction in recipe.items():
            deduction = float(item_deduction) * quantity
            inventory_item = Inventory.query.filter_by(item_name=item_name).first()
            if inventory_item:
                inventory_item.quantity -= deduction
                if inventory_item.quantity < inventory_item.low_stock_threshold:
                    print(f"!!! تنبيه: مخزون {item_name} منخفض جداً !!!")
        db.session.commit()
    return True

# ==========================================
# 3. واجهات المستخدم (Routes)
# ==========================================

@app.route('/')
def home():
    products_by_category = {}
    cats = db.session.query(Product.category).distinct().all()
    for cat in cats:
        cat_name = cat[0]
        products_by_category[cat_name] = Product.query.filter_by(category=cat_name).all()
    return render_template('pos.html', products_by_category=products_by_category)

@app.route('/create_order', methods=['POST'])
def create_order():
    data = request.json
    try:
        table_num = data['table_num']
        order_items_raw = data['items']
        
        total_amount = 0
        order_items_for_db = []

        for item_raw in order_items_raw:
            product = Product.query.get(item_raw['id'])
            item_total = product.price * item_raw['qty']
            total_amount += item_total
            order_items_for_db.append(f"{product.name} ({item_raw['qty']}x)")
            
            deduct_inventory(product.id, item_raw['qty'])
        
        service_charge = total_amount * 0.12
        final_total = total_amount + service_charge
        
        new_order = Order(
            table_num=table_num,
            total_amount=total_amount,
            final_total=final_total,
            items=json.dumps(order_items_for_db)
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        print(f"** تم طباعة فاتورة للطاولة {table_num} بمبلغ {final_total:.2f} **")
        
        return jsonify({"status": "success", "order_id": new_order.id, "final_total": final_total}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/admin')
def admin():
    # جلب البيانات من قاعدة البيانات
    products = Product.query.all()
    inventory = Inventory.query.all()
    orders = Order.query.order_by(Order.timestamp.desc()).limit(10).all()
    employees = Employee.query.all()
    
    # حساب إجمالي المبيعات اليوم
    today = datetime.now().date()
    today_orders = Order.query.filter(Order.timestamp >= today).all()
    today_total = sum(order.final_total for order in today_orders)
    
    return render_template('admin.html', products=products, inventory=inventory, 
                           orders=orders, employees=employees, today_total=today_total)

@app.route('/test')
def test():
    """صفحة اختبار للتحقق من التصميم"""
    return app.send_static_file('test.html')

@app.route('/update_price', methods=['POST'])
def update_price():
    data = request.form
    product = Product.query.get(data['product_id'])
    if product:
        product.price = float(data['new_price'])
        db.session.commit()
        return redirect(url_for('admin'))
    return "Product not found", 404

@app.route('/update_inventory', methods=['POST'])
def update_inventory():
    data = request.form
    item = Inventory.query.get(data['item_id'])
    if item:
        item.quantity += float(data['new_quantity'])
        db.session.commit()
        return redirect(url_for('admin'))
    return "Item not found", 404

@app.route('/add_employee', methods=['POST'])
def add_employee():
    data = request.form
    new_employee = Employee(
        name=data['name'],
        position=data['position'],
        shift=data['shift'],
        phone=data['phone']
    )
    db.session.add(new_employee)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/get_reports')
def get_reports():
    daily_sales = db.session.query(db.func.date(Order.timestamp), db.func.sum(Order.final_total)).group_by(db.func.date(Order.timestamp)).all()
    return jsonify({"daily_sales": daily_sales})

# ==========================================
# 4. مسارات الخادم البسيط المضافة (Simple Server Routes)
# ==========================================

@app.route('/index.html')
def index_page():
    """صفحة الرئيسية"""
    return send_from_directory('.', 'index.html')

@app.route('/menu.html')
def menu_page():
    """صفحة القائمة"""
    return send_from_directory('.', 'menu.html')

@app.route('/qr.html')
def qr_page():
    """صفحة QR Code"""
    return send_from_directory('.', 'qr.html')

@app.route('/admin.html')
def admin_html_page():
    """صفحة Admin HTML"""
    return send_from_directory('.', 'admin.html')

@app.route('/pos')
def pos_redirect():
    """تحويل إلى صفحة POS"""
    return redirect(url_for('home'))

@app.route('/templates/pos.html')
def pos_template():
    """صفحة POS من Templates"""
    return render_template('pos.html', products_by_category={})

@app.route('/templates/admin.html')
def admin_template():
    """صفحة Admin من Templates"""
    return redirect(url_for('admin'))

# API endpoints للخادم البسيط
@app.route('/api/menu')
def api_menu():
    """API للقائمة"""
    products = Product.query.all()
    menu_data = []
    for product in products:
        menu_data.append({
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'price': product.price
        })
    return jsonify(menu_data)

@app.route('/api/prices')
def api_prices():
    """API للأسعار"""
    products = Product.query.all()
    prices = {}
    for product in products:
        prices[product.name] = product.price
    return jsonify(prices)

# ==========================================
# 5. مسارات QR Code الديناميكية (QR Code Routes)
# ==========================================

@app.route('/qr/image')
def qr_image():
    """خدمة صورة QR Code الحقيقية"""
    try:
        return send_file('smile_cafe_qr_real.png', mimetype='image/png')
    except FileNotFoundError:
        # إذا لم تكن الصورة موجودة، قم بإنشائها
        import subprocess
        subprocess.run(['python', 'generate_qr.py'], cwd='.')
        return send_file('smile_cafe_qr_real.png', mimetype='image/png')

@app.route('/qr/generate')
def generate_qr_api():
    """API لإنشاء QR Code ديناميكي"""
    try:
        import subprocess
        subprocess.run(['python', 'generate_qr.py'], cwd='.')
        return jsonify({'status': 'success', 'message': 'QR Code generated successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==========================================
# 6. تطبيقات المحمول وشاشات العرض (Mobile Apps & Displays)
# ==========================================

@app.route('/mobile')
def mobile_app():
    """تطبيق الجرسونات للموبايل"""
    return send_from_directory('.', 'mobile_app.html')

@app.route('/kitchen')
def kitchen_display():
    """شاشة المطبخ"""
    return send_from_directory('.', 'kitchen_display.html')

@app.route('/cashier')
def cashier_display():
    """شاشة الكاشير"""
    return render_template('admin.html')

@app.route('/api/orders')
def api_orders():
    """API للطلبات للمطبخ والكاشير"""
    orders = Order.query.order_by(Order.timestamp.desc()).all()
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': order.id,
            'table_num': order.table_num,
            'items': order.items,
            'status': order.status,
            'timestamp': order.timestamp.isoformat() if order.timestamp else None,
            'final_total': order.final_total,
            'priority': False  # يمكن إضافة منطق الأولوية لاحقاً
        })
    return jsonify(orders_data)

@app.route('/complete_order/<int:order_id>', methods=['POST'])
def complete_order(order_id):
    """إكمال الطلب من المطبخ"""
    order = Order.query.get(order_id)
    if order:
        order.status = 'Completed'
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Order not found'}), 404

@app.route('/toggle_priority/<int:order_id>', methods=['POST'])
def toggle_priority(order_id):
    """تغيير أولوية الطلب"""
    order = Order.query.get(order_id)
    if order:
        # يمكن إضافة حقل priority في قاعدة البيانات
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Order not found'}), 404

# ==========================================
# 4. تهيئة قاعدة البيانات بالمنيو (Smile Menu)
# ==========================================

def setup_smile_cafe_data():
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully!")

    if Product.query.first(): 
        print("Database already contains data. Skipping initialization.")
        return

    raw_materials = [
        {"name": "بن", "unit": "جم"},
        {"name": "حليب", "unit": "مل"},
        {"name": "سكر", "unit": "جم"},
        {"name": "كوب ورقي", "unit": "قطعة"},
        {"name": "شاي", "unit": "جم"},
        {"name": "شاي أخضر", "unit": "جم"},
        {"name": "شاي فتلة", "unit": "جم"},
        {"name": "نعناع", "unit": "جم"},
        {"name": "زنجبيل", "unit": "جم"},
        {"name": "قرفة", "unit": "جم"},
        {"name": "يانسون", "unit": "جم"},
        {"name": "كركديه", "unit": "جم"},
        {"name": "ليمون", "unit": "جم"},
        {"name": "مليسة", "unit": "جم"},
        {"name": "بابونج", "unit": "جم"},
        {"name": "خروب", "unit": "جم"},
        {"name": "سحلب", "unit": "جم"},
        {"name": "ثلج", "unit": "جم"},
        {"name": "شوكولاتة", "unit": "جم"},
        {"name": "كراميل", "unit": "مل"},
        {"name": "فانيليا", "unit": "مل"},
        {"name": "أوريو", "unit": "جم"},
        {"name": "نوتيلا", "unit": "جم"},
        {"name": "فراولة", "unit": "جم"},
        {"name": "مانجو", "unit": "جم"},
        {"name": "خوخ", "unit": "جم"},
        {"name": "كرز", "unit": "جم"},
        {"name": "جوافة", "unit": "جم"},
        {"name": "أناناس", "unit": "جم"},
        {"name": "برتقال", "unit": "جم"},
        {"name": "تفاح", "unit": "جم"},
        {"name": "موز", "unit": "جم"},
        {"name": "توت", "unit": "جم"},
        {"name": "جزر", "unit": "جم"},
        {"name": "عسل", "unit": "مل"},
        {"name": "جرانولا", "unit": "جم"},
        {"name": "مكسرات", "unit": "جم"},
        {"name": "بروتين", "unit": "جم"},
        {"name": "كنز", "unit": "مل"},
        {"name": "كوكاكولا", "unit": "مل"},
        {"name": "بيبسي", "unit": "مل"},
        {"name": "سفن أب", "unit": "مل"},
        {"name": "ميرندا", "unit": "مل"},
        {"name": "اندراق", "unit": "مل"},
        {"name": "مياه", "unit": "مل"},
        {"name": "مياه غازية", "unit": "مل"},
        {"name": "فرخة", "unit": "جم"},
        {"name": "كفتة", "unit": "جم"},
        {"name": "برجر", "unit": "جم"},
        {"name": "أرز", "unit": "جم"},
        {"name": "بطاطس", "unit": "جم"},
        {"name": "خضروات", "unit": "جم"},
        {"name": "عيش", "unit": "رغيف"},
        {"name": "جبن", "unit": "جم"},
        {"name": "عجينة بيتزا", "unit": "جم"},
        {"name": "صلصة", "unit": "مل"},
        {"name": "كريب", "unit": "قطعة"},
        {"name": "بانيه", "unit": "جم"},
        {"name": "كرانشي", "unit": "جم"},
        {"name": "هوت دوج", "unit": "جم"},
        {"name": "بطاطس سوري", "unit": "جم"},
        {"name": "تفاح معسل فاخر", "unit": "جم"},
        {"name": "خوخ معسل فاخر", "unit": "جم"},
        {"name": "كريز معسل فاخر", "unit": "جم"},
        {"name": "ميكس VIP", "unit": "جم"},
        {"name": "ميكس عادي", "unit": "جم"},
        {"name": "فحم", "unit": "قطعة"},
        {"name": "لي طبي", "unit": "قطعة"},
        {"name": "زبادي", "unit": "مل"},
        {"name": "فواكه", "unit": "جم"},
        {"name": "قنبلة سمايل", "unit": "قطعة"},
    ]
    for mat in raw_materials:
        db.session.add(Inventory(item_name=mat['name'], quantity=5000, unit=mat['unit']))
    
    smile_menu = [
        # 1. قسم المشروبات الساخنة (Hot Drinks)
        {"name": "قهوة تركي", "cat": "ساخن", "price": 35, "recipe": {"بن": 10, "سكر": 5, "كوب ورقي": 1}},
        {"name": "قهوة تركي محوج", "cat": "ساخن", "price": 40, "recipe": {"بن": 12, "حليب": 50, "سكر": 5, "كوب ورقي": 1}},
        {"name": "قهوة باللبن", "cat": "ساخن", "price": 50, "recipe": {"بن": 10, "حليب": 100, "سكر": 8, "كوب ورقي": 1}},
        {"name": "قهوة فرنساوي", "cat": "ساخن", "price": 55, "recipe": {"بن": 15, "سكر": 5, "كوب ورقي": 1}},
        {"name": "قهوة بندق / شوكولاتة", "cat": "ساخن", "price": 45, "recipe": {"بن": 12, "شوكولاتة": 10, "سكر": 5, "كوب ورقي": 1}},
        {"name": "نسكافيه (بلاك)", "cat": "ساخن", "price": 40, "recipe": {"نسكافيه": 10, "سكر": 5, "كوب ورقي": 1}},
        {"name": "نسكافيه (جولد)", "cat": "ساخن", "price": 45, "recipe": {"نسكافيه": 12, "حليب": 50, "سكر": 5, "كوب ورقي": 1}},
        {"name": "نسكافيه (3*1)", "cat": "ساخن", "price": 45, "recipe": {"نسكافيه": 15, "حليب": 30, "سكر": 5, "كوب ورقي": 1}},
        {"name": "كابتشينو (S)", "cat": "ساخن", "price": 60, "recipe": {"بن": 12, "حليب": 120, "سكر": 5, "كوب ورقي": 1}},
        {"name": "كابتشينو (L)", "cat": "ساخن", "price": 70, "recipe": {"بن": 18, "حليب": 180, "سكر": 8, "كوب ورقي": 1}},
        {"name": "لاتيه", "cat": "ساخن", "price": 65, "recipe": {"بن": 12, "حليب": 150, "سكر": 5, "كوب ورقي": 1}},
        {"name": "هوت شوكلت", "cat": "ساخن", "price": 65, "recipe": {"شوكولاتة": 30, "حليب": 150, "سكر": 10, "كوب ورقي": 1}},
        {"name": "سحلب سادة", "cat": "ساخن", "price": 55, "recipe": {"سحلب": 20, "حليب": 150, "سكر": 10, "كوب ورقي": 1}},
        {"name": "سحلب فواكه", "cat": "ساخن", "price": 65, "recipe": {"سحلب": 20, "حليب": 150, "فواكه": 30, "سكر": 10, "كوب ورقي": 1}},
        {"name": "شاي سادة", "cat": "ساخن", "price": 20, "recipe": {"شاي": 2, "سكر": 5, "كوب ورقي": 1}},
        {"name": "شاي فتلة", "cat": "ساخن", "price": 25, "recipe": {"شاي فتلة": 3, "سكر": 5, "كوب ورقي": 1}},
        {"name": "شاي أخضر", "cat": "ساخن", "price": 25, "recipe": {"شاي أخضر": 2, "سكر": 5, "كوب ورقي": 1}},
        
        # 2. قسم المشروبات المثلجة والفرابيه (Iced & Frappe)
        {"name": "آيس كوفي", "cat": "مثلج", "price": 65, "recipe": {"بن": 12, "ثلج": 50, "حليب": 100, "سكر": 8, "كوب ورقي": 1}},
        {"name": "آيس لاتيه", "cat": "مثلج", "price": 70, "recipe": {"بن": 12, "ثلج": 50, "حليب": 150, "سكر": 8, "كوب ورقي": 1}},
        {"name": "آيس موكا", "cat": "مثلج", "price": 75, "recipe": {"بن": 12, "شوكولاتة": 20, "ثلج": 50, "حليب": 100, "سكر": 10, "كوب ورقي": 1}},
        {"name": "فرابيه أوريو", "cat": "مثلج", "price": 75, "recipe": {"حليب": 150, "ثلج": 50, "أوريو": 20, "سكر": 10, "كوب ورقي": 1}},
        {"name": "فرابيه كراميل", "cat": "مثلج", "price": 75, "recipe": {"حليب": 150, "ثلج": 50, "كراميل": 20, "سكر": 10, "كوب ورقي": 1}},
        {"name": "فرابيه موكا", "cat": "مثلج", "price": 75, "recipe": {"بن": 10, "شوكولاتة": 20, "ثلج": 50, "حليب": 100, "سكر": 10, "كوب ورقي": 1}},
        {"name": "سموزي مانجو", "cat": "مثلج", "price": 60, "recipe": {"مانجو": 100, "حليب": 100, "ثلج": 30, "سكر": 10, "كوب ورقي": 1}},
        {"name": "سموزي فراولة", "cat": "مثلج", "price": 60, "recipe": {"فراولة": 100, "حليب": 100, "ثلج": 30, "سكر": 10, "كوب ورقي": 1}},
        {"name": "سموزي خوخ", "cat": "مثلج", "price": 60, "recipe": {"خوخ": 100, "حليب": 100, "ثلج": 30, "سكر": 10, "كوب ورقي": 1}},
        {"name": "ميلك شيك فانيليا", "cat": "مثلج", "price": 70, "recipe": {"حليب": 200, "ثلج": 30, "فانيليا": 10, "سكر": 15, "كوب ورقي": 1}},
        {"name": "ميلك شيك شوكولاتة", "cat": "مثلج", "price": 70, "recipe": {"حليب": 200, "ثلج": 30, "شوكولاتة": 30, "سكر": 15, "كوب ورقي": 1}},
        {"name": "ميلك شيك مانجو", "cat": "مثلج", "price": 70, "recipe": {"حليب": 200, "ثلج": 30, "مانجو": 50, "سكر": 15, "كوب ورقي": 1}},
        
        # 3. قسم الوجبات (Meals)
        {"name": "وجبة أولى (ربع فرخة)", "cat": "وجبة", "price": 180, "recipe": {"فرخة": 250, "أرز": 200, "بطاطس": 100, "خضروات": 100, "عيش": 2}},
        {"name": "وجبة ثانية (2 قطعة برجر)", "cat": "وجبة", "price": 190, "recipe": {"برجر": 200, "أرز": 200, "بطاطس": 100, "خضروات": 100, "عيش": 2}},
        {"name": "وجبة ثالثة (نصف فرخة)", "cat": "وجبة", "price": 240, "recipe": {"فرخة": 500, "أرز": 200, "بطاطس": 100, "خضروات": 100, "عيش": 2}},
        {"name": "وجبة رابعة (1/8 كفتة + ربع فرخة)", "cat": "وجبة", "price": 210, "recipe": {"كفتة": 125, "فرخة": 250, "أرز": 200, "بطاطس": 100, "خضروات": 100, "عيش": 2}},
        {"name": "وجبة خامسة (1/4 كفتة + ربع فرخة)", "cat": "وجبة", "price": 230, "recipe": {"كفتة": 250, "فرخة": 250, "أرز": 200, "بطاطس": 100, "خضروات": 100, "عيش": 2}},
        {"name": "وجبة سادسة (ربع فرخة + ربع كفتة)", "cat": "وجبة", "price": 250, "recipe": {"فرخة": 250, "كفتة": 250, "أرز": 200, "بطاطس": 100, "خضروات": 100, "عيش": 2}},
        
        # 4. قسم البيتزا والكريب (Pizza & Crepe)
        {"name": "بيتزا مارجريتا (M)", "cat": "بيتزا", "price": 120, "recipe": {"عجينة بيتزا": 150, "صلصة": 50, "جبن": 80}},
        {"name": "بيتزا مارجريتا (L)", "cat": "بيتزا", "price": 140, "recipe": {"عجينة بيتزا": 200, "صلصة": 70, "جبن": 120}},
        {"name": "بيتزا مشكل جبن (M)", "cat": "بيتزا", "price": 140, "recipe": {"عجينة بيتزا": 150, "صلصة": 50, "جبن": 120}},
        {"name": "بيتزا مشكل جبن (L)", "cat": "بيتزا", "price": 160, "recipe": {"عجينة بيتزا": 200, "صلصة": 70, "جبن": 160}},
        {"name": "بيتزا فراخ (M)", "cat": "بيتزا", "price": 160, "recipe": {"عجينة بيتزا": 150, "صلصة": 50, "فرخة": 100, "جبن": 80}},
        {"name": "بيتزا فراخ (L)", "cat": "بيتزا", "price": 180, "recipe": {"عجينة بيتزا": 200, "صلصة": 70, "فرخة": 120, "جبن": 120}},
        {"name": "بيتزا لحمة (M)", "cat": "بيتزا", "price": 160, "recipe": {"عجينة بيتزا": 150, "صلصة": 50, "لحمة": 100, "جبن": 80}},
        {"name": "بيتزا لحمة (L)", "cat": "بيتزا", "price": 180, "recipe": {"عجينة بيتزا": 200, "صلصة": 70, "لحمة": 120, "جبن": 120}},
        {"name": "كريب نوتيلا (S)", "cat": "كريب", "price": 60, "recipe": {"كريب": 1, "نوتيلا": 40}},
        {"name": "كريب نوتيلا (L)", "cat": "كريب", "price": 80, "recipe": {"كريب": 2, "نوتيلا": 60}},
        {"name": "كريب فراخ بانيه (S)", "cat": "كريب", "price": 110, "recipe": {"كريب": 1, "فرخة": 80, "بانيه": 30}},
        {"name": "كريب فراخ بانيه (L)", "cat": "كريب", "price": 130, "recipe": {"كريب": 2, "فرخة": 100, "بانيه": 40}},
        {"name": "كريب كرانشي (S)", "cat": "كريب", "price": 110, "recipe": {"كريب": 1, "فراخة": 80, "كرانشي": 30}},
        {"name": "كريب كرانشي (L)", "cat": "كريب", "price": 130, "recipe": {"كريب": 2, "فراخة": 100, "كرانشي": 40}},
        {"name": "كريب مشكل لحوم (S)", "cat": "كريب", "price": 140, "recipe": {"كريب": 1, "فراخة": 50, "كفتة": 50, "لحمة": 50}},
        {"name": "كريب مشكل لحوم (L)", "cat": "كريب", "price": 160, "recipe": {"كريب": 2, "فراخة": 70, "كفتة": 70, "لحمة": 70}},
        
        # 5. قسم السندوتشات (Sandwiches)
        {"name": "برجر سادة", "cat": "سندوتش", "price": 80, "recipe": {"برجر": 100, "عيش": 1, "خضروات": 30}},
        {"name": "برجر جبنة", "cat": "سندوتش", "price": 95, "recipe": {"برجر": 100, "جبن": 30, "عيش": 1, "خضروات": 30}},
        {"name": "فراخ بانيه", "cat": "سندوتش", "price": 90, "recipe": {"فرخة": 100, "بانيه": 20, "عيش": 1, "خضروات": 30}},
        {"name": "فراخ كرانشي", "cat": "سندوتش", "price": 90, "recipe": {"فرخة": 100, "كرانشي": 20, "عيش": 1, "خضروات": 30}},
        {"name": "هوت دوج", "cat": "سندوتش", "price": 75, "recipe": {"هوت دوج": 80, "عيش": 1, "خضروات": 20}},
        {"name": "بطاطس سوري", "cat": "سندوتش", "price": 50, "recipe": {"بطاطس سوري": 150, "خضروات": 30}},
        
        # 6. قسم الشيشة والمعسل (Shisha)
        {"name": "حجر فاخر تفاح", "cat": "شيشة", "price": 90, "recipe": {"تفاح معسل فاخر": 20, "فحم": 3}},
        {"name": "حجر فاخر خوخ", "cat": "شيشة", "price": 90, "recipe": {"خوخ معسل فاخر": 20, "فحم": 3}},
        {"name": "حجر فاخر كريز", "cat": "شيشة", "price": 90, "recipe": {"كريز معسل فاخر": 20, "فحم": 3}},
        {"name": "حجر فاخر عنب", "cat": "شيشة", "price": 90, "recipe": {"عنب معسل فاخر": 20, "فحم": 3}},
        {"name": "حجر فاخر فراولة", "cat": "شيشة", "price": 90, "recipe": {"فراولة معسل فاخر": 20, "فحم": 3}},
        {"name": "حجر فاخر مانجو", "cat": "شيشة", "price": 90, "recipe": {"مانجو معسل فاخر": 20, "فحم": 3}},
        {"name": "حجر فاخر جوافة", "cat": "شيشة", "price": 90, "recipe": {"جوافة معسل فاخر": 20, "فحم": 3}},
        {"name": "حجر فاخر برتقال", "cat": "شيشة", "price": 90, "recipe": {"برتقال معسل فاخر": 20, "فحم": 3}},
        {"name": "حجر فاخر ليمون", "cat": "شيشة", "price": 90, "recipe": {"ليمون معسل فاخر": 20, "فحم": 3}},
        {"name": "حجر فاخر نعناع", "cat": "شيشة", "price": 90, "recipe": {"نعناع معسل فاخر": 20, "فحم": 3}},
        {"name": "حجر فاخر كركديه", "cat": "شيشة", "price": 90, "recipe": {"كركديه معسل فاخر": 20, "فحم": 3}},
        {"name": "حجر ميكس VIP", "cat": "شيشة", "price": 100, "recipe": {"ميكس VIP": 20, "فحم": 3}},
        {"name": "حجر ميكس عادي", "cat": "شيشة", "price": 80, "recipe": {"ميكس عادي": 20, "فحم": 3}},
        
        # 7. قسم الحلويات والكوكتيلات (Desserts & Cocktails)
        {"name": "فخفخينا (S)", "cat": "حلويات", "price": 70, "recipe": {"عيش": 2, "حليب": 100, "سكر": 20, "فواكه": 30}},
        {"name": "فخفخينا (L)", "cat": "حلويات", "price": 85, "recipe": {"عيش": 3, "حليب": 150, "سكر": 30, "فواكه": 50}},
        {"name": "زبادي خلاط سادة", "cat": "حلويات", "price": 55, "recipe": {"زبادي": 200, "حليب": 50, "سكر": 15, "كوب ورقي": 1}},
        {"name": "زبادي خلاط فواكه", "cat": "حلويات", "price": 65, "recipe": {"زبادي": 200, "حليب": 50, "فواكه": 50, "سكر": 15, "كوب ورقي": 1}},
        {"name": "قنبلة سمايل", "cat": "حلويات", "price": 120, "recipe": {"آيس كريم": 100, "شوكولاتة": 30, "صلصة": 20, "فواكه": 30, "قنبلة سمايل": 1}},
        {"name": "ميكس نوتيلا", "cat": "حلويات", "price": 100, "recipe": {"نوتيلا": 50, "آيس كريم": 80, "حليب": 50, "فواكه": 30}},
        
        # 8. قسم الخدمات والإضافات
        {"name": "إضافة لي طبي", "cat": "خدمة", "price": 25, "recipe": {"لي طبي": 1}},
        {"name": "أي إضافة أخرى", "cat": "خدمة", "price": 10, "recipe": {"إضافة": 1}},
        {"name": "إضافة جبنة", "cat": "خدمة", "price": 25, "recipe": {"جبن": 25}},
        {"name": "إضافة لحوم", "cat": "خدمة", "price": 40, "recipe": {"لحوم": 40}},
    ]
    
    for prod in smile_menu:
        recipe_json = json.dumps(prod['recipe']) if 'recipe' in prod else None
        db.session.add(Product(name=prod['name'], category=prod['cat'], price=prod['price'], recipe=recipe_json))
        
    db.session.commit()
    print(".. تم تحميل منيو Smile Cafe في قاعدة البيانات ..")

if __name__ == '__main__':
    with app.app_context():
        setup_smile_cafe_data()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)