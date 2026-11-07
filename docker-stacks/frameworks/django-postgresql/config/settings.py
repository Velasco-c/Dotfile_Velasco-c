import os
# Clave de ejemplo solo para desarrollo local; define DJANGO_SECRET_KEY fuera de este entorno.
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "app_local_secret")
DEBUG = True
ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = "config.urls"
INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.auth"]
DATABASES = {"default": {"ENGINE": "django.db.backends.postgresql", "HOST": "postgres", "NAME": os.getenv("POSTGRES_DB"), "USER": os.getenv("POSTGRES_USER"), "PASSWORD": os.getenv("POSTGRES_PASSWORD"), "PORT": "5432"}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
