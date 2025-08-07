from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_register_view, name='login_register'),
    path('logout/', views.logout_view, name='logout'),
    
    # ¡No hay URLs de API!
]