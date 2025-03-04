"""
Django settings for main project.

Generated by 'django-admin startproject' using Django 5.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path
import dj_database_url
import sys
from decouple import config
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJANGO_SECRET_KEY', default="django-insecure-dtm(&qi$!j_z_vgr26=o-v5*c93t$g-h@shxk%#znf8*^*oyx_")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Сторонние приложения
    "debug_toolbar",
    "rest_framework",

    # мои приложения
    'coffeehouses',
    'orders',
    'users',
    'api',

    # Другие приложения
    # 'livereload',
]

INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default="postgres://coffee_user:root@localhost:5432/Coffee_times",  # Это строка по умолчанию для локальной базы данных
        conn_max_age=600,
    )
    # {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'Coffee_times',
    #     'USER': 'coffee_user',
    #     'PASSWORD': 'root',
    #     'HOST': 'localhost',  # Или адрес сервера
    #     'PORT': '5432',       # Стандартный порт PostgreSQL
    # }
}

LOGIN_URL = '/user/login/'

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = [
    'users.backends.PhoneOrUsernameBackend'
]

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Kyiv'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

if 'test' in sys.argv:
    # Используем стандартное хранилище для тестов, чтобы избежать ошибок с манифестом
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "static", 'users'
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

UNFOLD = {
    "SITE_HEADER": "Админка",
    "TEXT": {
        "HEADER": "text-primary-500", # Молочный цвет для заголовков
        "PARAGRAPH": "text-gray-200",  # Светло-серый для основного текста
        "SECONDARY": "text-gray-400",  # Серый для второстепенного текста
    },
    "ELEMENTS": {
        "CARD": "bg-dark-400 border-dark-300", # Чуть светлее фон для карточек
        "TABLE": {
            "HEADER": "bg-dark-300",           # Фон заголовка таблицы
            "ROW": "hover:bg-dark-200",        # Подсветка строк при наведении
        }
    },
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "255 223 145",
            "600": "35 35 35",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "238 167 4",
            "950": "59 7 100",
        }, 
        "font": {
            "subtle-light": "107 114 128",
            "subtle-dark": "156 163 175",
            "default-light": "75 85 99",
            "default-dark": "209 213 219",
            "important-light": "17 24 39",
            "important-dark": "243 244 246",
        },
    },

    "STYLES": [
        lambda request: static("css/unfold.css"),
    ],


    "SITE_TITLE": 'Моя админка',  # Название панели

    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/svg+xml",
            "href": lambda request: static("icons/favicon.png"),
        },
    ],

    "SIDEBAR": {
        "show_search": True,  # Search in applications and models names
        "show_all_applications": True,  # Dropdown with all applications and models
        "navigation": [
            {
                "title": _("Navigation"),
                "separator": False,  # Top border
                "collapsible": False,  # Collapsible group of links
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:index"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title":_("Кавярні"),
                        "link": reverse_lazy("admin:coffeehouses_coffeehouse_changelist"),
                    },
                    {
                        "title":_("Столики"),
                        "link":reverse_lazy("admin:coffeehouses_table_changelist"),
                    },
                    {
                        "title":_("Категорії"),
                        "link": reverse_lazy("admin:coffeehouses_category_changelist"),
                    },
                    {
                        "title":_("Продукти"),
                        "link":reverse_lazy("admin:coffeehouses_product_changelist")
                    },
                    {
                        "title":_("Бронювання"),
                        "link": reverse_lazy("admin:orders_reservation_changelist"),
                    },
                    {
                        "title": _("Статистика"),
                        "link": reverse_lazy("admin:reservation_statistics")
                    },
                    {
                        "title": _("Пользователи"),
                        "icon": "people",
                        "link": reverse_lazy("admin:users_user_changelist"),
                    },
                ],
            },
        ],
    },
    
}