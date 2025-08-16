// static/tyzox/js/main.js

// ============================================
// TYZOX - SCRIPT PRINCIPAL UNIFICADO
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM cargado. Inicializando Tyzox...');

    // --- LÓGICA PARA LA PÁGINA DE INICIO (INDEX.HTML) ---
    const productGrid = document.getElementById('productGrid');
    if (productGrid) {
        console.log('Estás en la página de inicio. Cargando productos...');
        const allProducts = JSON.parse(document.getElementById('products-data').textContent);
        renderProducts(allProducts); // Render inicial

        // Asignar eventos a los filtros de categoría
        document.querySelectorAll('.category-card').forEach(card => {
            card.addEventListener('click', () => {
                const categorySlug = card.getAttribute('data-category-slug');
                renderProducts(allProducts, categorySlug);
            });
        });
    }

    // --- LÓGICA PARA LA PÁGINA DE LOGIN (LOGIN.HTML) ---
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        console.log('Estás en la página de login/registro.');
        // No necesitamos hacer nada aquí porque los eventos están en el HTML (onclick, onsubmit)
        // Las funciones handleLogin, switchTab, etc., ya estarán disponibles globalmente.
    }

    // --- LÓGICA COMÚN A TODAS LAS PÁGINAS ---
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
});


// ============================================
// FUNCIONES PARA LA PÁGINA DE INICIO
// ============================================

function renderProducts(products, categorySlug = 'all') {
    const productGrid = document.getElementById('productGrid');
    if (!productGrid) return;

    productGrid.innerHTML = ''; // Limpiamos la grilla

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
            <div class="product-image">
                <img src="${product.image_url || 'https://via.placeholder.com/300x200'}" alt="${product.name}" loading="lazy"/>
            </div>
            <div class="product-name">${product.name}</div>
            <div class="product-price">$${product.price}</div>
            <button class="btn-add-cart" onclick="addToCart(${product.id})">
                <i class="fas fa-cart-plus"></i> Agregar
            </button>
        `;
        productGrid.appendChild(card);
    });
}

function addToCart(productId) {
    showNotification(`Producto ${productId} agregado al carrito (simulado).`, 'success');
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

async function handleLogin(event) {
    event.preventDefault();
    // La lógica de handleLogin que ya tenías
    console.log("Manejando login...");
    // ... tu código de fetch a /api/login/ ...
}

async function handleRegister(event) {
    event.preventDefault();
    // La lógica de handleRegister que ya tenías
    console.log("Manejando registro...");
    // ... tu código de fetch a /api/register/ ...
}


// ============================================
// FUNCIONES AUXILIARES Y COMUNES
// ============================================

function showNotification(message, type = 'info', duration = 3000) {
    let notification = document.getElementById('notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        notification.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 9999; padding: 15px 20px;
            border-radius: 8px; color: white; font-weight: bold; opacity: 0;
            transform: translateY(-20px); transition: all 0.3s ease; max-width: 350px;
        `;
        document.body.appendChild(notification);
    }
    const styles = {
        success: 'background: linear-gradient(45deg, #4CAF50, #45a049);',
        error: 'background: linear-gradient(45deg, #f44336, #da190b);',
        info: 'background: linear-gradient(45deg, #ff6b35, #f7931e);'
    };
    notification.style.background = styles[type] || styles.info;
    notification.textContent = message;
    notification.style.opacity = '1';
    notification.style.transform = 'translateY(0)';
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-20px)';
    }, duration);
}

function showMessage(message, type = 'error') {
    hideMessages();
    const messageEl = document.getElementById(type + 'Message');
    messageEl.textContent = message;
    messageEl.style.display = 'block';
}

function hideMessages() {
    document.getElementById('errorMessage').style.display = 'none';
    document.getElementById('successMessage').style.display = 'none';
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
// === LÓGICA PARA ELIMINAR CON MODAL DE CONFIRMACIÓN ===
// ===================================================

// Función para obtener el CSRF token (esencial para peticiones POST en Django)
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
const csrftoken = getCookie('csrftoken');


document.addEventListener('DOMContentLoaded', () => {
    const deleteModal = document.getElementById('deleteConfirmModal');
    const modalText = document.getElementById('deleteModalText');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');

    // Comprobamos si estamos en el dashboard
    if (deleteModal) {
        // Añadimos un listener a todos los botones de eliminar
        document.querySelectorAll('.delete-btn').forEach(button => {
            button.addEventListener('click', (event) => {
                event.preventDefault();
                
                const url = button.dataset.url;
                const productName = button.dataset.productName;

                // Personalizamos el texto del modal y mostramos el modal
                modalText.innerHTML = `¿Estás seguro de que deseas eliminar permanentemente el producto <strong style="color: #ff6b35;">"${productName}"</strong>?`;
                deleteModal.style.display = 'flex';

                // Cuando se hace clic en "Confirmar", realizamos la petición fetch
                confirmDeleteBtn.onclick = () => {
                    fetch(url, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrftoken,
                            'Content-Type': 'application/json'
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            // Si el borrado fue exitoso, eliminamos la fila de la tabla
                            button.closest('tr').remove();
                            showNotification(data.message, 'success');
                        } else {
                            showNotification(data.message, 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showNotification('Ocurrió un error de red.', 'error');
                    })
                    .finally(() => {
                        // Ocultamos el modal
                        deleteModal.style.display = 'none';
                    });
                };
            });
        });

        // El botón de cancelar simplemente oculta el modal
        cancelDeleteBtn.onclick = () => {
            deleteModal.style.display = 'none';
        };
    }
});