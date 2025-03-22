from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'subscriptions',
    'drf_yasg',
    'corsheaders'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'playstation_backend.urls'

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

WSGI_APPLICATION = 'playstation_backend.wsgi.application'

CORS_ALLOWED_ORIGINS = [
    "http://91.135.156.149",
    "https://91.135.156.149",
    "http://localhost:3001",
    "https://localhost:3001",
    "https://psgamezz.ru"
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
   'accept',
   'accept-encoding',
   'accept-language',
   'authorization',
   'content-type',
   'dnt',
   'origin',
   'user-agent',
   'x-csrftoken',
   'x-requested-with',
   'sec-ch-ua',
   'sec-ch-ua-mobile',
   'sec-ch-ua-platform',
   'sec-fetch-dest',
   'sec-fetch-mode',
   'sec-fetch-site',
   'referer'
]

CORS_EXPOSE_HEADERS = [
   'access-control-allow-origin',
   'access-control-allow-credentials'
]

CORS_ALLOW_METHODS = [
   'DELETE',
   'GET',
   'OPTIONS',
   'PATCH',
   'POST',
   'PUT',
   'HEAD'
]


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('DB_NAME'),
#         'USER': os.getenv('DB_USER'),
#         'PASSWORD': os.getenv('DB_PASSWORD'),
#         'HOST': os.getenv('DB_HOST'),
#         'PORT': os.getenv('DB_PORT'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ROBOKASSA_MERCHANT_LOGIN = 'PSGAMEZZ.RU'

ROBOKASSA_PASSWORD1 = 'yu7gTpqYtZDKJ5X6T49m'
ROBOKASSA_PASSWORD2 = 'trFcj1mX1fKw47lolhP9'
ROBOKASSA_TEST_MODE = True
ROBOKASSA_TEST_PASSWORD1 = 'G6aPODIgpupDIL9y3Qq9'
ROBOKASSA_TEST_PASSWORD2 = 'X73rYXxKeF9XTvB2Rqb6'

ROBOKASSA_RESULT_URL = 'https://psgamezz.ru/api/payment/result/'
ROBOKASSA_SUCCESS_URL = 'https://psgamezz.ru/payment/success/'
ROBOKASSA_FAIL_URL = 'https://psgamezz.ru/payment/fail/'
