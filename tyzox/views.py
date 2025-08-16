# tyzox/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.db.models import Sum
from .models import Product, Category, Order, OrderItem, Cart, CartItem
from .forms import ProductForm
from itertools import combinations
import csv
import json

# tyzox/views.py

def index(request):
    products_queryset = Product.objects.filter(is_available=True).select_related('category')
    
    print("--- DEBUG: Verificando slugs de productos ---") # Mensaje para orientarnos
    
    products_list = []
    for product in products_queryset:
        # --- AÑADE ESTA LÍNEA DE DEBUG ---
        print(f"Producto: '{product.name}', Slug: '{product.slug}'")
        
        products_list.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'image_url': product.image_url,
            'category_slug': product.category.slug,
            'detail_url': product.get_absolute_url()
        })

    print("--- FIN DEBUG ---")
    
    context = { 'products': products_list }
    return render(request, 'tyzox/index.html', context)


def product_detail_view(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, is_available=True)
    related_products = product.related_products.filter(is_available=True).exclude(id=product.id)[:4]
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'tyzox/product_detail.html', context)

# ... (El resto de tus vistas: login, logout, dashboard, etc., van aquí sin cambios) ...
def login_register_view(request):
    if request.user.is_authenticated: return redirect('index')
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

@login_required
def dashboard_view(request):
    if not request.user.is_superuser: return redirect('index')
    products = Product.objects.all().order_by('name')
    context = { 'products': products }
    return render(request, 'tyzox/dashboard.html', context)

@login_required
def product_add_view(request):
    if not request.user.is_superuser: return redirect('index')
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
    if not request.user.is_superuser: return redirect('index')
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"El producto '{product.name}' ha sido actualizado.")
            return redirect('dashboard')
    else:
        form = ProductForm(instance=product)
    context = { 'form': form, 'product': product }
    return render(request, 'tyzox/product_form.html', context)

@login_required
def product_delete_view(request, product_id):
    if not request.user.is_superuser: return JsonResponse({'status': 'error', 'message': 'No tienes permiso.'}, status=403)
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        return JsonResponse({'status': 'success', 'message': f"El producto '{product_name}' ha sido eliminado."})
    return JsonResponse({'status': 'error', 'message': 'Petición no válida.'}, status=400)

@login_required
def reports_view(request):
    if not request.user.is_superuser: return redirect('index')
    sales_report = OrderItem.objects.values('product__name', 'product__category__name').annotate(total_sold=Sum('quantity'), total_revenue=Sum('price')).order_by('-total_sold')
    context = { 'sales_report': sales_report }
    return render(request, 'tyzox/reports.html', context)

@login_required
def export_sales_csv(request):
    if not request.user.is_superuser: return redirect('index')
    response = HttpResponse(content_type='text/csv', headers={'Content-Disposition': 'attachment; filename="reporte_ventas.csv"'})
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    writer.writerow(['Producto', 'Categoría', 'Unidades Vendidas', 'Ingresos Totales'])
    sales_report = OrderItem.objects.values('product__name', 'product__category__name').annotate(total_sold=Sum('quantity'), total_revenue=Sum('price')).order_by('-total_sold')
    for item in sales_report:
        writer.writerow([item['product__name'], item['product__category__name'], item['total_sold'], item['total_revenue']])
    return response

# ============================================
# --- VISTAS DE LA API PARA EL CARRITO DE COMPRAS ---
# ============================================

@login_required
def add_to_cart_api(request):
    # Solo aceptamos peticiones POST
    if request.method == 'POST':
        try:
            # Leemos los datos JSON enviados por el frontend
            data = json.loads(request.body)
            product_id = data.get('product_id')
            
            # Verificamos que el producto exista y esté disponible
            product = get_object_or_404(Product, id=product_id, is_available=True)
            
            # Obtenemos el carrito del usuario actual
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            # Buscamos si el producto ya está en el carrito para solo aumentar la cantidad
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product
            )
            
            if not created:
                # Si el item ya existía, incrementamos la cantidad
                cart_item.quantity += 1
            
            cart_item.save()
            
            # Devolvemos una respuesta de éxito con el nuevo total de items
            return JsonResponse({
                'status': 'success',
                'message': f"'{product.name}' añadido al carrito.",
                'item_count': cart.item_count
            })

        except Exception as e:
            # Si algo sale mal, devolvemos un error
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Petición no válida'}, status=400)


@login_required
def get_cart_api(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Preparamos los datos del carrito para enviarlos como JSON
    items_list = []
    for item in cart.items.all():
        items_list.append({
            'name': item.product.name,
            'quantity': item.quantity,
            'price': str(item.product.price),
            'subtotal': str(item.subtotal),
            'image_url': item.product.image_url
        })
        
    return JsonResponse({
        'status': 'success',
        'items': items_list,
        'total': str(cart.total),
        'item_count': cart.item_count
    })

# ============================================
# --- VISTA DE API PARA FINALIZAR LA COMPRA ---
# ============================================
@login_required
@transaction.atomic
def checkout_api(request):
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.all()
            products_in_order = [item.product for item in cart_items] # Obtenemos los productos ANTES de borrar los items

            if not cart_items.exists():
                return JsonResponse({'status': 'error', 'message': 'Tu carrito está vacío.'}, status=400)

            # 1. Crear la Orden principal
            new_order = Order.objects.create(
                user=request.user,
                total_price=cart.total
            )

            # 2. Mover cada item del carrito a un item de la orden
            for item in cart_items:
                OrderItem.objects.create(
                    order=new_order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price * item.quantity # Guardamos el precio total del item
                )

            # 3. Vaciar el carrito de compras
            cart_items.delete()

            # --- ¡LÓGICA DEL GRAFO MOVIDA AQUÍ! ---
            # 4. Ahora que la orden está completa, actualizamos el grafo.
            if len(products_in_order) >= 2:
                product_pairs = combinations(products_in_order, 2)
                for p1, p2 in product_pairs:
                    p1.related_products.add(p2)
            # --- FIN DE LA LÓGICA DEL GRAFO ---
            
            return JsonResponse({
                'status': 'success',
                'message': f'¡Compra completada! Tu número de orden es #{new_order.id}.',
                'order_id': new_order.id
            })

        except Cart.DoesNotExist:
             return JsonResponse({'status': 'error', 'message': 'No se encontró tu carrito.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Ocurrió un error inesperado: {str(e)}'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Petición no válida'}, status=400)