"""
Django settings for license_plate_recognition project.

Generated by 'django-admin startproject' using Django 4.1.13.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-o@q5oofxmopd(f3ue(zyh%v$zsyrlh1hba$g3&t(vl&eij0&te'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'license_plate_recognition.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'license_plate_recognition.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # hoặc 'django.db.backends.mysql'
        'NAME': 'bien_so_db',
        'USER': 'root',
        'PASSWORD': 'newpassword',         # hoặc password nếu có
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_TZ = True
TIME_ZONE = 'Asia/Ho_Chi_Minh'


USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Nếu bạn muốn phục vụ các file static trong quá trình phát triển:
import os
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'core/static'),
]
# Cấu hình đăng nhập

# Cấu hình email (ví dụ dùng console backend để test)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Hoặc cấu hình email thật (ví dụ với Gmail)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-password'
# Media files (ảnh biển số lưu lại)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Templates
TEMPLATES[0]['DIRS'] = [BASE_DIR / 'core/templates']
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'
AUTH_USER_MODEL = 'core.User'
# Cấu hình thời gian
# settings.py
TIME_ZONE = 'Asia/Ho_Chi_Minh'  # Múi giờ Việt Nam
USE_I18N = True
USE_L10N = True
USE_TZ = True  # Sử dụng múi giờ tự động
# settings.py
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Session settings (cho chức năng "Ghi nhớ đăng nhập")
SESSION_COOKIE_AGE = 1209600 if DEBUG else 3600  # 2 tuần (debug) hoặc 1 giờ
SESSION_SAVE_EVERY_REQUEST = True
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# import cloudinary
# from pathlib import Path
# DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# # Cloudinary configuration
# CLOUDINARY_STORAGE ={
#     'CLOUD_NAME':'dlbx77zwt',  # Replace with your Cloudinary cloud name
#     'API_KEY':'768853479554589',        # Replace with your Cloudinary API key
#     'API_SECRET':'rgZA3TTEp-7n5U7sPKvke8M1sHU',  # Replace with your Cloudinary API secret
# }
# settings.py

import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    cloud_name='dlbx77zwt',
    api_key='768853479554589',
    api_secret='rgZA3TTEp-7n5U7sPKvke8M1sHU',
)

