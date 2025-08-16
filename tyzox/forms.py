# tyzox/forms.py

from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    # Hacemos que el campo de categoría sea un menú desplegable
    # y nos aseguramos de que muestre los nombres de las categorías.
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Categoría",
        widget=forms.Select(attrs={'class': 'form-control'}) # 'form-control' es una clase común para styling
    )

    class Meta:
        model = Product
        # Lista de los campos del modelo que queremos en nuestro formulario
        fields = ['category', 'name', 'description', 'price', 'image_url', 'stock', 'is_available']
        # Etiquetas personalizadas para que se vean bien en español
        labels = {
            'name': 'Nombre del Producto',
            'description': 'Descripción',
            'price': 'Precio',
            'image_url': 'URL de la Imagen',
            'stock': 'Inventario (Stock)',
            'is_available': 'Está Disponible para la Venta',
        }
        # Widgets para darle un poco de estilo o cambiar el tipo de input
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}), # Hace el campo de descripción más grande
        }