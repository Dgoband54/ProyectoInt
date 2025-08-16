# tyzox/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from itertools import combinations

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Categoría")
    slug = models.SlugField(max_length=100, unique=True, help_text="Versión del nombre amigable para URLs")
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['name']
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name="Categoría")
    name = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    slug = models.SlugField(max_length=200, unique=True, help_text="Versión amigable para URL (ej: guantes-profesionales-everlast)")
    description = models.TextField(verbose_name="Descripción", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    image_url = models.URLField(max_length=1024, blank=True, null=True, verbose_name="URL de la Imagen")
    stock = models.PositiveIntegerField(default=0, verbose_name="Inventario")
    is_available = models.BooleanField(default=True, verbose_name="Está Disponible")
    related_products = models.ManyToManyField('self', blank=True, symmetrical=True, verbose_name="Productos Relacionados")
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['name']
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'product_slug': self.slug})

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

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE, verbose_name="Carrito")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    def __str__(self):
        return f"{self.quantity} x {self.product.name} en {self.cart}"
    @property
    def subtotal(self):
        return self.quantity * self.product.price

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

@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)
