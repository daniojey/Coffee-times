from .settings import *

DEBUG = True

ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS += [os.environ.get('HEROKU_APP_NAME', '') + '.herokuapp.com']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True  # Для работы через HTTPS
CSRF_COOKIE_SECURE = True     # Для защиты от CSRF-атак
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SAMESITE = 'None'  # Было 'Lax'
CSRF_COOKIE_SAMESITE = 'None'     # Добавлено


SECURE_HSTS_SECONDS = 3600  # 1 час
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

CSRF_COOKIE_HTTPONLY = False  # Разрешить доступ к куке из JS
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'  # Совпадает с фронтендом
CSRF_COOKIE_NAME = 'csrftoken'
SESSION_COOKIE_NAME = 'sessionid'