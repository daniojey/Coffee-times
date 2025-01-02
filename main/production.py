from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Coffee_times',
        'USER': 'coffee_user',
        'PASSWORD': 'root',
        'HOST': 'db',  # Или адрес сервера
        'PORT': '5432',       # Стандартный порт PostgreSQL
    }
}