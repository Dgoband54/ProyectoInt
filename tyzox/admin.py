# tyzox/admin.py

from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem

# Usaremos decoradores para un registro más limpio y potente
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)} # Autocompleta el slug basado en el nombre

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')
    # Para la relación ManyToMany, es mejor usar filter_horizontal
    filter_horizontal = ('related_products',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_price')
    list_filter = ('created_at', 'user')

# También puedes registrar los otros modelos si quieres verlos en el admin
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)