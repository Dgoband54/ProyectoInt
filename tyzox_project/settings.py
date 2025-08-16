# tyzox_project/settings.py

import os
from pathlib import Path

# ==============================================================================
# CONFIGURACIÓN BÁSICA DEL PROYECTO
# ==============================================================================

# La ruta base de tu proyecto. Django la usa para encontrar otros archivos.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# ==============================================================================

# ¡IMPORTANTE! Nunca compartas esta clave. En producción, cárgala desde una variable de entorno.
SECRET_KEY = 'django-insecure-n_poylu0!092w&8olx(bx%gyqa!ec4vi-8xw(a@g298r+tn(4^'

# DEBUG = True te muestra páginas de error detalladas.
# En producción, SIEMPRE debe estar en False.
DEBUG = True

# En producción, aquí debes poner el dominio de tu sitio web, ej: ['www.tyzox.com']
ALLOWED_HOSTS = []


# ==============================================================================
# DEFINICIÓN DE APLICACIONES
# ==============================================================================

# Aquí le dices a Django qué "piezas" o apps componen tu proyecto.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Tu aplicación principal
    'tyzox',
]


# ==============================================================================
# MIDDLEWARE
# ==============================================================================

# Capas de procesamiento que manejan las peticiones y respuestas.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ==============================================================================
# CONFIGURACIÓN DE URLs Y WSGI
# ==============================================================================

# El archivo principal que define las URLs de tu proyecto.
ROOT_URLCONF = 'tyzox_project.urls'

# La puerta de entrada para que los servidores web se comuniquen con tu app.
WSGI_APPLICATION = 'tyzox_project.wsgi.application'


# ==============================================================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ==============================================================================

# Tus credenciales para conectar con PostgreSQL.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tyzox_db',
        'USER': 'tyzox_user',
        'PASSWORD': '1234',   # ¡RECUERDA CAMBIAR ESTO EN PRODUCCIÓN!
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# ==============================================================================
# CONFIGURACIÓN DE PLANTILLAS (TEMPLATES)
# ==============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # APP_DIRS = True le dice a Django que busque plantillas dentro de cada app (ej. tyzox/templates/)
        'DIRS': [], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ==============================================================================
# VALIDACIÓN DE CONTRASEÑAS
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# ==============================================================================
# INTERNACIONALIZACIÓN (IDIOMA Y ZONA HORARIA)
# ==============================================================================

LANGUAGE_CODE = 'es' # Español
TIME_ZONE = 'UTC'    # Puedes cambiarla a tu zona horaria, ej: 'America/Guayaquil'
USE_I18N = True
USE_TZ = True


# ==============================================================================
# CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS (CSS, JAVASCRIPT)
# ==============================================================================

# La URL base desde la que se servirán los archivos estáticos.
STATIC_URL = '/static/'

# ¡¡ESTA ES LA CORRECCIÓN CLAVE!!
# Aquí le decimos a Django que busque archivos estáticos adicionales
# en la carpeta 'static' que está DENTRO de tu aplicación 'tyzox'.
STATICFILES_DIRS = [
    BASE_DIR / "tyzox/static",
]


# ==============================================================================
# CONFIGURACIÓN DE AUTENTICACIÓN
# ==============================================================================

# Si un usuario no logueado intenta acceder a una página protegida,
# Django lo redirigirá a la URL con el nombre 'login_register'.
LOGIN_URL = 'login_register'


# ==============================================================================
# CONFIGURACIÓN POR DEFECTO DE CLAVE PRIMARIA
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'