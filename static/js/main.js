// ملف JavaScript الرئيسي لنظام Smile Cafe POS

// المتغيرات العامة
let orderItems = [];
let selectedProducts = new Set();
let currentTable = '';
let isOnline = navigator.onLine;

// تهيئة الصفحة
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkConnectivity();
    startAutoRefresh();
});

// تهيئة التطبيق
function initializeApp() {
    console.log('جاري تهيئة نظام Smile Cafe POS...');
    
    // تحميل البيانات الأولية
    loadInitialData();
    
    // إعداد تأثيرات الحركة
    setupAnimations();
    
    // تهيئة التخزين المحلي
    initializeLocalStorage();
    
    console.log('تم تهيئة النظام بنجاح');
}

// إعداد مستمعي الأحداث
function setupEventListeners() {
    // أحداث لوحة المفاتيح
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // أحداث الاتصال
    window.addEventListener('online', () => updateConnectionStatus(true));
    window.addEventListener('offline', () => updateConnectionStatus(false));
    
    // أحداث النموذج
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // أحداث البحث
    const searchInputs = document.querySelectorAll('input[type="search"], input[placeholder*="ابحث"]');
    searchInputs.forEach(input => {
        input.addEventListener('input', handleSearch);
    });
}

// تحميل البيانات الأولية
async function loadInitialData() {
    try {
        showLoading();
        
        // تحميل المنتجات
        await loadProducts();
        
        // تحميل المخزون
        await loadInventory();
        
        // تحميل الطلبات الأخيرة
        await loadRecentOrders();
        
        hideLoading();
        
    } catch (error) {
        console.error('خطأ في تحميل البيانات:', error);
        showError('فشل في تحميل البيانات الأولية');
        hideLoading();
    }
}

// اختصارات لوحة المفاتيح
function handleKeyboardShortcuts(event) {
    // Ctrl + N: طلب جديد
    if (event.ctrlKey && event.key === 'n') {
        event.preventDefault();
        clearOrder();
    }
    
    // Ctrl + S: حفظ/تأكيد الطلب
    if (event.ctrlKey && event.key === 's') {
        event.preventDefault();
        confirmOrder();
    }
    
    // Ctrl + A: لوحة التحكم
    if (event.ctrlKey && event.key === 'a') {
        event.preventDefault();
        window.location.href = '/admin';
    }
    
    // Escape: إلغاء
    if (event.key === 'Escape') {
        closeAllModals();
    }
    
    // F1: مساعدة
    if (event.key === 'F1') {
        event.preventDefault();
        showHelp();
    }
}

// إدارة المنتجات
function toggleProduct(productId, productName, productPrice) {
    const card = document.querySelector(`[onclick="toggleProduct(${productId}"]`);
    
    if (selectedProducts.has(productId)) {
        selectedProducts.delete(productId);
        card.classList.remove('selected');
        removeOrderItem(productId);
        playSound('remove');
    } else {
        selectedProducts.add(productId);
        card.classList.add('selected');
        addOrderItem(productId, productName, productPrice);
        playSound('add');
    }
    
    updateOrderDisplay();
    saveOrderToLocalStorage();
}

function addOrderItem(productId, productName, productPrice) {
    const existingItem = orderItems.find(item => item.id === productId);
    
    if (existingItem) {
        existingItem.quantity++;
        showNotification(`تم زيادة ${productName}`, 'success');
    } else {
        orderItems.push({
            id: productId,
            name: productName,
            price: productPrice,
            quantity: 1
        });
        showNotification(`تم إضافة ${productName}`, 'success');
    }
}

function removeOrderItem(productId) {
    const itemIndex = orderItems.findIndex(item => item.id === productId);
    if (itemIndex > -1) {
        const item = orderItems[itemIndex];
        if (item.quantity > 1) {
            item.quantity--;
            showNotification(`تم إنقاص ${item.name}`, 'info');
        } else {
            orderItems.splice(itemIndex, 1);
            showNotification(`تم حذف ${item.name}`, 'warning');
        }
    }
}

function updateOrderDisplay() {
    const orderItemsContainer = document.getElementById('orderItems');
    if (!orderItemsContainer) return;
    
    orderItemsContainer.innerHTML = '';
    
    if (orderItems.length === 0) {
        orderItemsContainer.innerHTML = '<div class="text-center text-muted">لا توجد منتجات في الطلب</div>';
        updateOrderSummary(0);
        return;
    }
    
    let subtotal = 0;
    
    orderItems.forEach(item => {
        const itemTotal = item.price * item.quantity;
        subtotal += itemTotal;
        
        const itemElement = createOrderItemElement(item);
        orderItemsContainer.appendChild(itemElement);
    });
    
    updateOrderSummary(subtotal);
}

function createOrderItemElement(item) {
    const div = document.createElement('div');
    div.className = 'order-item';
    div.innerHTML = `
        <div class="order-item-name">${item.name}</div>
        <div class="order-item-quantity">
            <button class="quantity-btn" onclick="decreaseQuantity(${item.id})">
                <i class="fas fa-minus"></i>
            </button>
            <span>${item.quantity}</span>
            <button class="quantity-btn" onclick="increaseQuantity(${item.id})">
                <i class="fas fa-plus"></i>
            </button>
            <span class="item-total">${(item.price * item.quantity).toFixed(2)} ج.م</span>
        </div>
    `;
    return div;
}

function updateOrderSummary(subtotal) {
    const service = subtotal * 0.12;
    const total = subtotal + service;
    
    const subtotalElement = document.getElementById('subtotal');
    const serviceElement = document.getElementById('service');
    const totalElement = document.getElementById('total');
    
    if (subtotalElement) subtotalElement.textContent = `${subtotal.toFixed(2)} ج.م`;
    if (serviceElement) serviceElement.textContent = `${service.toFixed(2)} ج.م`;
    if (totalElement) totalElement.textContent = `${total.toFixed(2)} ج.م`;
}

function increaseQuantity(productId) {
    const item = orderItems.find(item => item.id === productId);
    if (item) {
        item.quantity++;
        updateOrderDisplay();
        saveOrderToLocalStorage();
        playSound('click');
    }
}

function decreaseQuantity(productId) {
    const item = orderItems.find(item => item.id === productId);
    if (item && item.quantity > 1) {
        item.quantity--;
        updateOrderDisplay();
        saveOrderToLocalStorage();
        playSound('click');
    } else if (item && item.quantity === 1) {
        const card = document.querySelector(`[onclick="toggleProduct(${productId}"]`);
        if (card) {
            card.classList.remove('selected');
            selectedProducts.delete(productId);
        }
        removeOrderItem(productId);
        updateOrderDisplay();
        saveOrderToLocalStorage();
        playSound('remove');
    }
}

function clearOrder() {
    if (orderItems.length > 0 && !confirm('هل أنت متأكد من مسح الطلب الحالي؟')) {
        return;
    }
    
    orderItems = [];
    selectedProducts.clear();
    
    document.querySelectorAll('.product-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    updateOrderDisplay();
    clearLocalStorage();
    
    const tableInput = document.getElementById('tableNumber');
    if (tableInput) tableInput.value = '';
    
    showNotification('تم مسح الطلب', 'info');
    playSound('clear');
}

// تأكيد الطلب
async function confirmOrder() {
    const tableNumber = document.getElementById('tableNumber')?.value;
    
    if (!tableNumber) {
        showNotification('يرجى إدخال رقم الطاولة', 'error');
        shakeElement('tableNumber');
        return;
    }
    
    if (orderItems.length === 0) {
        showNotification('يرجى اختيار منتجات على الأقل', 'error');
        return;
    }
    
    const orderData = {
        table_num: tableNumber,
        items: orderItems.map(item => ({
            id: item.id,
            qty: item.quantity
        }))
    };
    
    try {
        showLoading();
        
        const response = await fetch('/create_order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showSuccessMessage(result);
            clearOrder();
            printReceipt(result);
            playSound('success');
        } else {
            showNotification('حدث خطأ: ' + result.message, 'error');
        }
        
    } catch (error) {
        console.error('خطأ في تأكيد الطلب:', error);
        showNotification('حدث خطأ في الاتصال بالخادم', 'error');
    } finally {
        hideLoading();
    }
}

function showSuccessMessage(result) {
    const successMessage = document.getElementById('successMessage');
    if (successMessage) {
        successMessage.style.display = 'block';
        successMessage.innerHTML = `
            <i class="fas fa-check-circle"></i> 
            تم تأكيد الطلب بنجاح! 
            رقم الطلب: ${result.order_id} | الإجمالي: ${result.final_total.toFixed(2)} ج.م
        `;
        
        setTimeout(() => {
            successMessage.style.display = 'none';
        }, 5000);
    }
}

// طباعة الفاتورة
function printReceipt(orderData) {
    // يمكن إضافة وظيفة الطباعة هنا
    console.log('جاري طباعة الفاتورة:', orderData);
    
    // محاكاة الطباعة
    if (window.print) {
        window.print();
    }
}

// البحث
function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    const targetSelector = event.target.dataset.target;
    
    if (!targetSelector) return;
    
    const elements = document.querySelectorAll(targetSelector);
    
    elements.forEach(element => {
        const text = element.textContent.toLowerCase();
        const row = element.closest('tr');
        
        if (text.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// الإشعارات
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // إضافة تأثير الحركة
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // إزالة الإشعار بعد 3 ثواني
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// التأثيرات الحركية
function setupAnimations() {
    // إضافة تأثيرات الدخول للبطاقات
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    });
    
    document.querySelectorAll('.card-custom, .product-card, .stat-card').forEach(card => {
        observer.observe(card);
    });
}

function shakeElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add('shake');
        setTimeout(() => {
            element.classList.remove('shake');
        }, 500);
    }
}

// الأصوات
function playSound(type) {
    // يمكن إضافة الأصوات هنا
    const sounds = {
        add: 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT',
        remove: 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT',
        click: 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT',
        success: 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT',
        clear: 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT'
    };
    
    const audio = new Audio(sounds[type] || sounds.click);
    audio.volume = 0.3;
    audio.play().catch(e => console.log('فشل تشغيل الصوت:', e));
}

// التخزين المحلي
function initializeLocalStorage() {
    if (!localStorage.getItem('smileCafePOS')) {
        localStorage.setItem('smileCafePOS', JSON.stringify({
            version: '1.0.0',
            settings: {
                autoSave: true,
                soundEnabled: true,
                animationsEnabled: true
            }
        }));
    }
}

function saveOrderToLocalStorage() {
    const settings = JSON.parse(localStorage.getItem('smileCafePOS'));
    if (settings.settings.autoSave) {
        localStorage.setItem('currentOrder', JSON.stringify({
            items: orderItems,
            table: currentTable,
            timestamp: new Date().toISOString()
        }));
    }
}

function loadOrderFromLocalStorage() {
    const savedOrder = localStorage.getItem('currentOrder');
    if (savedOrder) {
        const order = JSON.parse(savedOrder);
        const orderAge = new Date() - new Date(order.timestamp);
        
        // استعادة الطلب إذا كان أقدم من 30 دقيقة
        if (orderAge < 30 * 60 * 1000) {
            orderItems = order.items || [];
            currentTable = order.table || '';
            
            if (document.getElementById('tableNumber')) {
                document.getElementById('tableNumber').value = currentTable;
            }
            
            updateOrderDisplay();
            showNotification('تم استعادة الطلب المحفوظ', 'info');
        } else {
            clearLocalStorage();
        }
    }
}

function clearLocalStorage() {
    localStorage.removeItem('currentOrder');
}

// فحص الاتصال
function checkConnectivity() {
    updateConnectionStatus(navigator.onLine);
}

function updateConnectionStatus(isConnected) {
    isOnline = isConnected;
    
    const statusElement = document.getElementById('connectionStatus');
    if (statusElement) {
        statusElement.className = isConnected ? 'online' : 'offline';
        statusElement.textContent = isConnected ? 'متصل' : 'غير متصل';
    }
    
    if (!isConnected) {
        showNotification('انقطع الاتصال بالإنترنت', 'warning');
    } else {
        showNotification('تم استعادة الاتصال', 'success');
    }
}

// التحديث التلقائي
function startAutoRefresh() {
    setInterval(() => {
        if (isOnline) {
            syncData();
        }
    }, 30000); // كل 30 ثانية
}

async function syncData() {
    try {
        // مزامنة البيانات مع الخادم
        await loadRecentOrders();
        await loadInventory();
    } catch (error) {
        console.error('فشل مزامنة البيانات:', error);
    }
}

// تحميل البيانات من الخادم
async function loadProducts() {
    // يتم تحميل المنتجات من الخادم
    console.log('تحميل المنتجات...');
}

async function loadInventory() {
    // يتم تحميل المخزون من الخادم
    console.log('تحميل المخزون...');
}

async function loadRecentOrders() {
    // يتم تحميل الطلبات الأخيرة من الخادم
    console.log('تحميل الطلبات الأخيرة...');
}

// معالجة النماذج
function handleFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // إضافة معالجة النموذج هنا
    console.log('إرسال النموذج:', formData);
}

// المودال
function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        const bootstrapModal = bootstrap.Modal.getInstance(modal);
        if (bootstrapModal) {
            bootstrapModal.hide();
        }
    });
}

// التحميل
function showLoading() {
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.style.display = 'flex';
    }
}

function hideLoading() {
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
}

// عرض الخطأ
function showError(message) {
    showNotification(message, 'error');
}

// المساعدة
function showHelp() {
    alert(`اختصارات لوحة المفاتيح:
    
Ctrl + N: طلب جديد
Ctrl + S: حفظ/تأكيد الطلب
Ctrl + A: لوحة التحكم
Escape: إغلاق النوافذ
F1: عرض المساعدة

معلومات الاتصال: ${isOnline ? 'متصل' : 'غير متصل'}`);
}

// التصدير
window.SmileCafePOS = {
    orderItems,
    selectedProducts,
    currentTable,
    isOnline,
    toggleProduct,
    confirmOrder,
    clearOrder,
    showNotification
};
