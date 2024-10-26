"""
Django settings for food project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-787!lb)3qfpc=9n@(0jxkj-ft#ppz4ycc!ip7dkfa6smzsc*p0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# DEBUG = False

# ALLOWED_HOSTS = []



# ALLOWED_HOSTS = ['food.onrender.com']


# ALLOWED_HOSTS = ['food.onrender.com', 'www.food.onrender.com', 'food-7ie2.onrender.com']


# ALLOWED_HOSTS = [
#     'food.onrender.com', 
#     'www.food.onrender.com', 
#     'food-7ie2.onrender.com',
#     'localhost', 
#     '127.0.0.1',
# ]



import os

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
#last two lines newly added


ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'firebase_admin'
]

EXTERNAL_APPS = [ 'home',
                 'accounts'
                 ]
INSTALLED_APPS += EXTERNAL_APPS


AUTH_USER_MODEL = 'accounts.CustomUser'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this line

]

ROOT_URLCONF = 'food.urls'

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

WSGI_APPLICATION = 'food.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }



# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'postgres',       # Database name
#         'USER': 'postgres.ispriplgvqmhodhundda',       # Database username
#         'PASSWORD': 'e4e5Nf3Nc6@',        # Database password
#         'HOST': 'aws-0-ap-southeast-1.pooler.supabase.com',            # Supabase PostgreSQL host (like db.xxxxx.supabase.co)
#         'PORT': '6543',                     # PostgreSQL port (usually 5432)
#     }
# }



import os

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
#last two lines newly added


# Get the PORT environment variable with a default value of '8000'
PORT = os.getenv("PORT", "8000")


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),  # Set in Render
        'USER': os.getenv('DATABASE_USER'),  # Set in Render
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),  # Set in Render
        'HOST': os.getenv('DATABASE_HOST'),  # Set in Render
        'PORT': os.getenv('DATABASE_PORT'),  # Set in Render
    }
}






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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/


import os

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# STATIC_URL = 'static/'
STATIC_URL = '/static/'
STATIC_ROOT =os.path.join(BASE_DIR,'staticfiles')

STATICFILES_DIRS =[
    os.path.join(BASE_DIR, 'home/static')
]
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

FIREBASE_SERVICE_ACCOUNT_KEY = os.path.join(BASE_DIR, 'config', 'firebase_credentials.json')  # Adjust the filename if necessary
FIREBASE_DATABASE_URL = 'https://dine-9153a-default-rtdb.asia-southeast1.firebasedatabase.app/'  # Your Firebase database URL
#Newly added

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
