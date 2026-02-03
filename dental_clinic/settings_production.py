"""
Production settings for dental_clinic project.
"""

from .settings import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
# Generate a new secret key with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-$!@bgg+$)x0tzg1w)#pkrk%40g6fgzm4-0abj+_xj+^-x$m+7-')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    # Add your domain here
    # 'yourdomain.com',
    # 'www.yourdomain.com',
    # Add your server IP here
    # 'your.server.ip',
]

# Database
# For production, you can use PostgreSQL or MySQL
# Uncomment and configure if needed:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'dental_clinic_db',
#         'USER': 'dental_clinic_user',
#         'PASSWORD': os.environ.get('DB_PASSWORD'),
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# STATICFILES_DIRS 不应该包含已经在 STATIC_ROOT 中的目录
# 只在源代码中有 static 目录时才需要
if (BASE_DIR / 'static').exists():
    STATICFILES_DIRS = [BASE_DIR / 'static']
else:
    STATICFILES_DIRS = []

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security settings
SECURE_SSL_REDIRECT = False  # Set to True when using HTTPS
SESSION_COOKIE_SECURE = False  # Set to True when using HTTPS
CSRF_COOKIE_SECURE = False  # Set to True when using HTTPS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS settings (uncomment when SSL is configured)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django_errors.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
