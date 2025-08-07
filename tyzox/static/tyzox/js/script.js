// ================================
// TYZOX - JavaScript Mejorado
// ================================

// Variables globales mejoradas
let token = localStorage.getItem('token') || null;
let currentUser = JSON.parse(localStorage.getItem('user')) || null;
let cart = [];

// Configuración de la API - Cambiar según tu backend
const API_BASE_URL = '/api'; // Para Django/PHP

// ================================
// UTILIDADES Y CONFIGURACIÓN
// ================================
const getHeaders = (includeAuth = false) => {
    const headers = { 'Content-Type': 'application/json' };
    if (includeAuth && token) {
        headers['Authorization'] = `Token ${token}`; // Sintaxis para Django Rest Framework
    }
    return headers;
};

const handleApiError = async (response) => {
    if (!response.ok) {
        let errorMessage = 'Error en la conexión';
        try {
            const errorData = await response.json();
            errorMessage = errorData.message || errorData.error || errorData.detail || errorMessage;
        } catch (e) {
            console.warn('No se pudo parsear el error:', e);
        }
        throw new Error(errorMessage);
    }
    return response.json();
};

const showNotification = (message, type = 'info', duration = 3000) => {
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
};

// ================================
// GESTIÓN DE AUTENTICACIÓN
// ================================
const updateLoginUI = () => {
    const loginLink = document.getElementById('loginLink');
    if (loginLink) {
        if (currentUser) {
            loginLink.innerHTML = `<i class="fas fa-user"></i> Hola, ${currentUser.name || currentUser.username}`;
            // Aquí puedes agregar un menú de usuario o un enlace al perfil
        } else {
            loginLink.innerHTML = '<i class="fas fa-sign-in-alt"></i> Iniciar Sesión';
        }
    }
};

const logout = () => {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    cart = [];
    updateLoginUI();
    updateCartCount();
    showNotification('Has cerrado sesión correctamente', 'info');
};


// ================================
// GESTIÓN DE PRODUCTOS
// ================================
const sampleProducts = [
    { id: 1, nombre: "Guantes Profesionales Everlast", precio: 89.99, categoria: "guantes", imagen: "https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80" },
    { id: 2, nombre: "Saco de Boxeo Heavy Bag", precio: 199.99, categoria: "sacos", imagen: "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80" },
    { id: 3, nombre: "Casco Protector Pro", precio: 129.99, categoria: "proteccion", imagen: "https://images.unsplash.com/photo-1517438476312-10d79c077509?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80" },
    { id: 4, nombre: "Shorts de Boxeo Premium", precio: 45.99, categoria: "ropa", imagen: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80" },
    { id: 5, nombre: "Pera de Velocidad", precio: 75.50, categoria: "sacos", imagen: "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80" },
    { id: 6, nombre: "Vendas de Boxeo", precio: 15.99, categoria: "proteccion", imagen: "https://images.unsplash.com/photo-1566478989037-eec170784d0b?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80" }
];

const renderProducts = async (filter = 'all') => {
    const productGrid = document.getElementById('productGrid');
    if (!productGrid) return;
    
    productGrid.innerHTML = '<p>Cargando productos...</p>';
    
    try {
        // En un entorno real, harías un fetch a tu API de Django.
        // const response = await fetch(`${API_BASE_URL}/products/`);
        // let products = await handleApiError(response);
        let products = sampleProducts; // Usando datos de ejemplo por ahora

        productGrid.innerHTML = '';
        const filteredProducts = filter === 'all' ? products : products.filter(p => p.categoria === filter);

        if (filteredProducts.length === 0) {
            productGrid.innerHTML = '<p>No se encontraron productos.</p>';
            return;
        }

        filteredProducts.forEach(product => {
            const card = document.createElement('div');
            card.className = 'product-card';
            card.innerHTML = `
                <div class="product-image">
                    <img src="${product.imagen || 'https://via.placeholder.com/300x200'}" alt="${product.nombre}" loading="lazy"/>
                </div>
                <div class="product-name">${product.nombre}</div>
                <div class="product-price">$${product.precio}</div>
                <button class="btn-add-cart" onclick="addToCart(${product.id})">
                    <i class="fas fa-cart-plus"></i> Agregar
                </button>
            `;
            productGrid.appendChild(card);
        });
    } catch (error) {
        console.error('Error al renderizar productos:', error);
        productGrid.innerHTML = `<p>Error al cargar productos. Intenta de nuevo.</p>`;
    }
};

const filterProducts = (category) => {
    renderProducts(category);
};

// ================================
// GESTIÓN DEL CARRITO
// ================================
const addToCart = (productId) => {
    if (!token) {
        showNotification('Por favor, inicia sesión para añadir al carrito', 'info');
        // Opcional: redirigir al login
        // window.location.href = '/login'; 
        return;
    }
    console.log(`Añadiendo producto ${productId} al carrito.`);
    showNotification('Producto agregado (simulado)', 'success');
    // Aquí iría la lógica fetch para añadir al carrito en el backend
};

const updateCartCount = () => {
    // Lógica para obtener el número de items del backend y actualizar #cartCount
};

const openCart = () => {
     if (!token) {
        showNotification('Inicia sesión para ver tu carrito', 'info');
        return;
    }
    openModal('cartModal');
    // Aquí iría la lógica fetch para obtener los items del carrito y mostrarlos
};

// ================================
// BÚSQUEDA
// ================================
let searchTimeout;
const performSearch = () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        const query = document.getElementById('searchInput')?.value.toLowerCase().trim();
        if (!query) {
            renderProducts();
            return;
        }
        const filtered = sampleProducts.filter(p => p.nombre.toLowerCase().includes(query));
        // Aquí puedes adaptar la función renderProducts para que acepte un array de productos
        console.log("Resultados de búsqueda:", filtered);
    }, 300);
};

// ================================
// GESTIÓN DE MODALES
// ================================
const openModal = (id, data = null) => {
    const modal = document.getElementById(id);
    if (!modal) return;
    
    if (id === 'routineModal' && data) {
        const routines = {
            principiante: { title: 'Fundamentos del Boxeo', desc: '...' },
            intermedio: { title: 'Técnica Avanzada', desc: '...' },
            profesional: { title: 'Preparación de Combate', desc: '...' }
        };
        const routine = routines[data];
        if (routine) {
            document.getElementById('routineTitle').textContent = routine.title;
            document.getElementById('routineDescription').textContent = routine.desc;
        }
    }
    
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
};

const closeModal = (id) => {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
};

// ================================
// EVENT LISTENERS Y INICIALIZACIÓN
// ================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM cargado. Inicializando Tyzox...');
    
    updateLoginUI();
    renderProducts();
    
    const hamburger = document.querySelector('.hamburger');
    const nav = document.querySelector('.nav-links');
    hamburger.addEventListener('click', () => {
        nav.classList.toggle('nav-active');
    });

    window.onclick = (event) => {
        if (event.target.classList.contains('modal')) {
            closeModal(event.target.id);
        }
    };
});