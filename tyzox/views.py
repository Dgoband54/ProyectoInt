from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Product

# Vista para la página de inicio
def index(request):
    # 1. Obtiene todos los productos disponibles de la base de datos
    products = Product.objects.filter(is_available=True)
    
    # 2. Pasa la lista de productos a la plantilla a través del 'context'
    context = {
        'products': products
    }
    return render(request, 'tyzox/index.html', context)

# Vista para el registro y el login (unificada para simplicidad)
def login_register_view(request):
    # Si el usuario ya está logueado, lo redirigimos a la página principal
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        # Comprueba qué formulario se envió
        form_type = request.POST.get('form_type')

        if form_type == 'register':
            # Lógica de registro
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                messages.error(request, 'Las contraseñas no coinciden.')
                return redirect('login_register')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Ya existe un usuario con este email.')
                return redirect('login_register')

            # Crea el usuario (usando el email como username)
            user = User.objects.create_user(username=email, email=email, password=password)
            messages.success(request, '¡Cuenta creada! Ahora puedes iniciar sesión.')
            return redirect('login_register')

        elif form_type == 'login':
            # Lógica de login
            email = request.POST.get('email')
            password = request.POST.get('password')

            try:
                username = User.objects.get(email=email).username
            except User.DoesNotExist:
                messages.error(request, 'El email o la contraseña son incorrectos.')
                return redirect('login_register')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('index') # ¡Redirección exitosa al index!
            else:
                messages.error(request, 'El email o la contraseña son incorrectos.')
                return redirect('login_register')

    # Si es una petición GET, simplemente muestra la página
    return render(request, 'tyzox/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')