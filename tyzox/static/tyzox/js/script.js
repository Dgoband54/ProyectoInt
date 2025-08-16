// static/tyzox/js/script.js

// ============================================
// TYZOX - SCRIPT PRINCIPAL UNIFICADO
// ============================================

// --- LÓGICA DE INICIALIZACIÓN PRINCIPAL ---
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM cargado. Inicializando Tyzox...');

    if (document.getElementById('productGrid')) {
        initializeHomePage();
    }
    if (document.getElementById('loginForm')) {
        console.log('Estás en la página de login/registro.');
    }
    initializeCommon();
    setupDeleteModal();
    updateCartBadgeOnLoad();
});

function initializeHomePage() {
    console.log('Inicializando página de inicio...');
    const allProducts = JSON.parse(document.getElementById('products-data').textContent);
    renderProducts(allProducts);
    document.querySelectorAll('.category-card').forEach(card => {
        card.addEventListener('click', () => {
            const categorySlug = card.getAttribute('data-category-slug');
            renderProducts(allProducts, categorySlug);
        });
    });
}

function initializeCommon() {
    const hamburger = document.querySelector('.hamburger');
    const nav = document.querySelector('.nav-links');
    if (hamburger && nav) {
        hamburger.addEventListener('click', () => {
            nav.classList.toggle('nav-active');
        });
    }
    window.onclick = (event) => {
        if (event.target.classList.contains('modal')) {
            closeModal(event.target.id);
        }
    };
}


// ============================================
// FUNCIONES PARA LA PÁGINA DE INICIO
// ============================================

function renderProducts(products, categorySlug = 'all') {
    const productGrid = document.getElementById('productGrid');
    if (!productGrid) return;
    productGrid.innerHTML = '';
    const filteredProducts = categorySlug === 'all'
        ? products
        : products.filter(p => p.category_slug === categorySlug);
    if (filteredProducts.length === 0) {
        productGrid.innerHTML = '<p>No se encontraron productos en esta categoría.</p>';
        return;
    }
    filteredProducts.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <a href="${product.detail_url}" style="text-decoration: none;">
                <div class="product-image">
                    <img src="${product.image_url || 'https://via.placeholder.com/300x200'}" alt="${product.name}" loading="lazy"/>
                </div>
                <div class="product-name" style="color: white;">${product.name}</div>
            </a>
            <div class="product-price">$${product.price}</div>
            <button class="btn-add-cart" onclick="addToCart(${product.id})">
                <i class="fas fa-cart-plus"></i> Agregar
            </button>
        `;
        productGrid.appendChild(card);
    });
}


// ============================================
// FUNCIONES PARA EL CARRITO DE COMPRAS
// ============================================

async function addToCart(productId) {
    const cartIcon = document.getElementById('cart-count-badge');
    if (!cartIcon) {
        showNotification('Por favor, inicia sesión para añadir productos al carrito.', 'info');
        return;
    }
    try {
        const response = await fetch('/api/cart/add/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
            body: JSON.stringify({ product_id: productId })
        });
        const data = await response.json();
        if (data.status === 'success') {
            showNotification(data.message, 'success');
            updateCartBadge(data.item_count);
        } else {
            showNotification(data.message || 'Hubo un error al añadir el producto.', 'error');
        }
    } catch (error) {
        console.error('Error en addToCart:', error);
        showNotification('Error de conexión con el servidor.', 'error');
    }
}

function updateCartBadge(count) {
    const badge = document.getElementById('cart-count-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-block' : 'none';
    }
}

async function openCartModal(event) {
    event.preventDefault();
    try {
        const response = await fetch('/api/cart/get/');
        const data = await response.json();
        if (data.status === 'success') {
            const cartItemsContainer = document.getElementById('cartItems');
            const cartTotalEl = document.getElementById('cartTotal');
            if (!cartItemsContainer || !cartTotalEl) return;
            cartItemsContainer.innerHTML = '';
            if (data.items.length === 0) {
                cartItemsContainer.innerHTML = '<p>Tu carrito está vacío.</p>';
            } else {
                data.items.forEach(item => {
                    const itemEl = document.createElement('div');
                    itemEl.innerHTML = `<div style="display: flex; gap: 1rem; align-items: center; border-bottom: 1px solid #444; padding-bottom: 1rem; margin-bottom: 1rem;">
                                            <img src="${item.image_url}" alt="${item.name}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 5px;">
                                            <div style="flex-grow: 1;">
                                                <div>${item.name}</div>
                                                <small>${item.quantity} x $${item.price}</small>
                                            </div>
                                            <strong>$${item.subtotal}</strong>
                                        </div>`;
                    cartItemsContainer.appendChild(itemEl);
                });
            }
            cartTotalEl.textContent = `Total: $${data.total}`;
            openModal('cartModal');
        } else {
            showNotification('No se pudo cargar el carrito.', 'error');
        }
    } catch (error) {
        console.error('Error en openCartModal:', error);
        showNotification('Error de conexión con el servidor.', 'error');
    }
}

function updateCartBadgeOnLoad() {
    const cartBadge = document.getElementById('cart-count-badge');
    if (cartBadge) {
        fetch('/api/cart/get/')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    updateCartBadge(data.item_count);
                }
            })
            .catch(err => console.error("No se pudo actualizar el carrito al cargar la página.", err));
    }
}


// ============================================
// FUNCIONES PARA LA PÁGINA DE LOGIN/REGISTRO
// ============================================

function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`.tab-btn[onclick="switchTab('${tab}')"]`).classList.add('active');
    document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));
    document.getElementById(tab + 'Form').classList.add('active');
    hideMessages();
}

function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.parentElement.querySelector('.password-toggle i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}


// ============================================
// FUNCIONES AUXILIARES Y COMUNES (MODALES, NOTIFICACIONES)
// ============================================

function showNotification(message, type = 'info', duration = 3000) {
    let notification = document.getElementById('notification');
    if (notification) {
        notification.remove();
    }

    notification = document.createElement('div');
    notification.id = 'notification';
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        padding: 16px 22px; /* Un poco más de padding */
        border-radius: 10px; /* Bordes más redondeados */
        color: white;
        font-family: Arial, sans-serif;
        font-size: 15px; /* Tamaño de fuente ligeramente ajustado */
        font-weight: bold;
        box-shadow: 0 5px 20px rgba(236, 236, 236, 0.25); /* Sombra un poco más pronunciada */
        
        /* --- ¡LA LÍNEA CLAVE! --- */
        border: 1px solid rgba(255, 255, 255, 0.15); 
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1); /* Transición más profesional */
        max-width: 350px;
        line-height: 1.4; /* Mejora la legibilidad en dos líneas */
    `;
    document.body.appendChild(notification);

    const styles = {
        success: 'background: linear-gradient(45deg, #4CAF50, #45a049);',
        error: 'background: linear-gradient(45deg, #f44336, #da190b);',
        info: 'background: linear-gradient(45deg, #ff6b35, #f7931e);'
    };
    notification.style.background = styles[type] || styles.info;
    notification.textContent = message;

    // Forzar reflow
    notification.offsetHeight; 

    // Animar entrada
    notification.style.opacity = '1';
    notification.style.transform = 'translateY(0)';

    // Programar salida
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(20px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 400);
    }, duration);
}
function showMessage(message, type = 'error') {
    // ... (sin cambios)
}

function hideMessages() {
    // ... (sin cambios)
}

function openModal(id) {
    const modal = document.getElementById(id);
    if(modal) modal.style.display = 'flex';
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if(modal) modal.style.display = 'none';
}


// ===================================================
// LÓGICA PARA ELIMINAR CON MODAL Y CSRF TOKEN (DASHBOARD)
// ===================================================

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function setupDeleteModal() {
    // ... (sin cambios)
}

// ============================================
// FUNCIONES PARA EL CARRITO DE COMPRAS
// ============================================

// ... (tus funciones addToCart, updateCartBadge, openCartModal van aquí) ...

// --- ¡AÑADE ESTA NUEVA FUNCIÓN! ---
async function checkout() {
    try {
        const response = await fetch('/api/cart/checkout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const data = await response.json();

        if (data.status === 'success') {
            // Si la compra fue exitosa
            closeModal('cartModal'); // Cierra el modal del carrito
            showNotification(data.message, 'success', 5000); // Muestra el mensaje de éxito por más tiempo
            updateCartBadge(0); // Reinicia el contador del carrito a 0
            
            // Opcional: redirigir a una página de "gracias" o a la página de inicio después de unos segundos
            // setTimeout(() => {
            //     window.location.href = '/';
            // }, 5000);

        } else {
            // Si hubo un error (ej: carrito vacío)
            showNotification(data.message || 'No se pudo procesar la compra.', 'error');
        }
    } catch (error) {
        console.error('Error en checkout:', error);
        showNotification('Error de conexión con el servidor.', 'error');
    }
}