// ================================
// LÓGICA PARA LOGIN Y REGISTRO
// ================================

// Cambiar entre pestañas de login y registro
function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`.tab-btn[onclick="switchTab('${tab}')"]`).classList.add('active');
    
    document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));
    document.getElementById(tab + 'Form').classList.add('active');
    
    hideMessages();
}

// Mostrar/ocultar contraseña
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

// Funciones para mostrar/ocultar mensajes de error/éxito
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

// Mostrar/ocultar spinner de carga
function showLoading(formType, show = true) {
    const btn = document.getElementById(formType + 'Btn');
    const originalText = formType === 'login' ? 'Iniciar Sesión' : 'Crear Cuenta';
    
    btn.disabled = show;
    if (show) {
        btn.innerHTML = `<span class="loading-spinner"></span> ${formType === 'login' ? 'Iniciando...' : 'Creando...'}`;
    } else {
        btn.innerHTML = originalText;
    }
}

// Función para obtener el CSRF token de las cookies (ESENCIAL PARA DJANGO)
function getCSRFToken() {
    let csrfToken = null;
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            csrfToken = value;
            break;
        }
    }
    return csrfToken;
}

// Manejar el envío del formulario de login
async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) {
        showMessage('Todos los campos son obligatorios.');
        return;
    }
    
    showLoading('login');

    try {
        const response = await fetch('/api/login/', { // Asegúrate que esta URL coincida con tu urls.py
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('¡Inicio de sesión exitoso! Redirigiendo...', 'success');
            if (data.token) {
                localStorage.setItem('token', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));
            }
            // Redirigir a la página de inicio
            setTimeout(() => {
                window.location.href = data.redirect_url || '/'; // Django puede enviar la URL a la que redirigir
            }, 1500);
        } else {
            showMessage(data.error || 'Credenciales incorrectas.');
        }
    } catch (error) {
        showMessage('Error de conexión. Por favor, inténtalo de nuevo.');
    } finally {
        showLoading('login', false);
    }
}

// Manejar el envío del formulario de registro
async function handleRegister(event) {
    event.preventDefault();
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (password !== confirmPassword) {
        showMessage('Las contraseñas no coinciden.');
        return;
    }
    if (password.length < 8) {
        showMessage('La contraseña debe tener al menos 8 caracteres.');
        return;
    }

    showLoading('register');

    try {
        const response = await fetch('/api/register/', { // Asegúrate que esta URL coincida con tu urls.py
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('¡Cuenta creada! Redirigiendo al login...', 'success');
            setTimeout(() => {
                switchTab('login'); // Cambiar a la pestaña de login
            }, 2000);
        } else {
            showMessage(data.error || 'No se pudo crear la cuenta.');
        }
    } catch (error) {
        showMessage('Error de conexión. Por favor, inténtalo de nuevo.');
    } finally {
        showLoading('register', false);
    }
}
