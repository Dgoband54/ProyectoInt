from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from itertools import combinations

# Modelo para las categorías de productos
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Categoría")
    slug = models.SlugField(max_length=100, unique=True, help_text="Versión del nombre amigable para URLs")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name

# Modelo para los productos
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name="Categoría")
    name = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    description = models.TextField(verbose_name="Descripción", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    image_url = models.URLField(max_length=1024, blank=True, null=True, verbose_name="URL de la Imagen")
    stock = models.PositiveIntegerField(default=0, verbose_name="Inventario")
    is_available = models.BooleanField(default=True, verbose_name="Está Disponible")
    
    # --- NUEVO CAMPO PARA EL GRAFO ---
    # Este campo crea la relación de "muchos a muchos" de un producto consigo mismo.
    # Aquí guardaremos los productos recomendados.
    related_products = models.ManyToManyField('self', blank=True, symmetrical=True, verbose_name="Productos Relacionados")
    # ------------------------------------

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['name']

    def __str__(self):
        return self.name

# Modelo para el Carrito de Compras de cada usuario
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.user.username}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

# Modelo para cada item dentro de un carrito
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE, verbose_name="Carrito")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} en {self.cart}"

    @property
    def subtotal(self):
        return self.quantity * self.product.price

# --- NUEVOS MODELOS PARA ÓRDENES ---
# Guardamos un registro de las compras para poder crear las relaciones
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Total")

    def __str__(self):
        return f"Orden #{self.id} de {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Orden")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} en Orden #{self.order.id}"
# ------------------------------------

# Señal que crea un Carrito automáticamente cada vez que se crea un nuevo Usuario.
@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)

# --- NUEVA SEÑAL PARA CONSTRUIR EL GRAFO ---
# Esta función se ejecutará cada vez que se guarde una nueva 'Order'.
@receiver(post_save, sender=Order)
def update_related_products(sender, instance, created, **kwargs):
    if created:
        # 1. Obtenemos todos los productos de la orden que se acaba de crear
        products_in_order = [item.product for item in instance.items.all()]

        # 2. Si hay 2 o más productos, creamos las conexiones
        if len(products_in_order) >= 2:
            # 3. Usamos 'combinations' para obtener todos los pares posibles de productos (ej: [A,B], [A,C], [B,C])
            product_pairs = combinations(products_in_order, 2)

            # 4. Para cada par, añadimos uno a la lista de 'related_products' del otro
            for p1, p2 in product_pairs:
                p1.related_products.add(p2)
                # p2.related_products.add(p1) # No es necesario por symmetrical=True
# ------------------------------------------------