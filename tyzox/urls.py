# tyzox/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # URLs de la tienda principal
    path('', views.index, name='index'),
    path('login/', views.login_register_view, name='login_register'),
    path('logout/', views.logout_view, name='logout'),

    # URLs del Dashboard de Administración
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/product/add/', views.product_add_view, name='product_add'),
    path('dashboard/product/edit/<int:product_id>/', views.product_edit_view, name='product_edit'),
    path('dashboard/product/delete/<int:product_id>/', views.product_delete_view, name='product_delete'),
    path('dashboard/reports/', views.reports_view, name='reports'),
    path('dashboard/reports/export/', views.export_sales_csv, name='export_sales_csv'),
]