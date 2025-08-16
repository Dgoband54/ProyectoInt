# tyzox/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum
import csv

# Importaciones de tu aplicación
from .models import Product, Category, OrderItem 
from .forms import ProductForm


# --- Vistas de la Tienda ---

def index(request):
    products_queryset = Product.objects.filter(is_available=True).select_related('category')
    
    products_list = []
    for product in products_queryset:
        products_list.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'image_url': product.image_url,
            'category_slug': product.category.slug,
        })

    context = { 'products': products_list }
    return render(request, 'tyzox/index.html', context)

def login_register_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'register':
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                messages.error(request, 'Las contraseñas no coinciden.')
                return redirect('login_register')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Ya existe un usuario con este email.')
                return redirect('login_register')

            user = User.objects.create_user(username=email, email=email, password=password)
            messages.success(request, '¡Cuenta creada! Ahora puedes iniciar sesión.')
            return redirect('login_register')

        elif form_type == 'login':
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
                return redirect('index')
            else:
                messages.error(request, 'El email o la contraseña son incorrectos.')
                return redirect('login_register')

    return render(request, 'tyzox/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

# --- Vistas del Dashboard ---

@login_required
def dashboard_view(request):
    if not request.user.is_superuser:
        return redirect('index')

    products = Product.objects.all().order_by('name')
    context = { 'products': products }
    return render(request, 'tyzox/dashboard.html', context)

@login_required
def product_add_view(request):
    if not request.user.is_superuser:
        return redirect('index')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"El producto '{form.cleaned_data['name']}' ha sido creado exitosamente.")
            return redirect('dashboard')
    else:
        form = ProductForm()

    context = { 'form': form }
    return render(request, 'tyzox/product_form.html', context)

@login_required
def product_edit_view(request, product_id):
    if not request.user.is_superuser:
        return redirect('index')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"El producto '{product.name}' ha sido actualizado.")
            return redirect('dashboard')
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product
    }
    return render(request, 'tyzox/product_form.html', context)

@login_required
def product_delete_view(request, product_id):
    if not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'No tienes permiso para realizar esta acción.'}, status=403)

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        return JsonResponse({
            'status': 'success', 
            'message': f"El producto '{product_name}' ha sido eliminado."
        })
    
    return JsonResponse({'status': 'error', 'message': 'Petición no válida.'}, status=400)
@login_required
def reports_view(request):
    if not request.user.is_superuser:
        return redirect('index')

    sales_report = OrderItem.objects.values(
        'product__name', 
        'product__category__name'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('price')
    ).order_by('-total_sold')

    context = {
        'sales_report': sales_report,
    }
    return render(request, 'tyzox/reports.html', context)

@login_required
def export_sales_csv(request):
    if not request.user.is_superuser:
        return redirect('index')

    # 1. Preparamos la respuesta HTTP para que el navegador la trate como un archivo descargable
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="reporte_ventas.csv"'},
    )
    response.write(u'\ufeff'.encode('utf8')) # BOM para que Excel entienda caracteres UTF-8 (acentos, etc.)

    # 2. Creamos un "escritor" de CSV que trabajará con nuestra respuesta HTTP
    writer = csv.writer(response)

    # 3. Escribimos la fila de encabezados
    writer.writerow(['Producto', 'Categoría', 'Unidades Vendidas', 'Ingresos Totales'])

    # 4. Realizamos la misma consulta de base de datos que en la vista del reporte
    sales_report = OrderItem.objects.values(
        'product__name', 
        'product__category__name'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('price')
    ).order_by('-total_sold')

    # 5. Escribimos los datos de cada producto en una nueva fila
    for item in sales_report:
        writer.writerow([
            item['product__name'],
            item['product__category__name'],
            item['total_sold'],
            item['total_revenue']
        ])

    return response