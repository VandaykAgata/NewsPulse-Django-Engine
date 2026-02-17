from pathlib import Path
import os
from dotenv import load_dotenv
from celery.schedules import crontab

# Загружаем переменные из .env
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Читаем секреты из .env
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Настройки почты
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # --- БЛОК ALLAUTH ---
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # --- ПРИЛОЖЕНИЯ (ниже allauth) ---
    'news.apps.NewsConfig',
    'accounts',
    'django_filters',
    'sign',
    'protect',
    'rest_framework',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'news.middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'NewsPaper.urls'

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

WSGI_APPLICATION = 'NewsPaper.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True  # Включаем поддержку перевода
USE_L10N = True  # Включаем форматирование чисел и дат под регион

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]
# Список языков, на которые мы будем переводить
LANGUAGES = [
    ('ru', 'Русский'),
    ('en-us', 'English'), # Добавь -us, как в админке!
]
USE_TZ = True
TIME_ZONE = 'UTC'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# --- Настройки Авторизации (для LoginRequiredMixin) ---

# 1. Адрес страницы входа (куда перенаправляется незалогиненный пользователь).

LOGIN_URL = '/accounts/login/'

# 2. Адрес, куда пользователь будет перенаправлен ПОСЛЕ успешного входа,
# если он не пытался открыть какую-то конкретную защищенную страницу.
# Мы перенаправляем на корень сайта
LOGIN_REDIRECT_URL = '/'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',

]

REST_FRAMEWORK = {
# По умолчанию читать могут все, а менять — только авторизованные
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}
SITE_ID = 1
ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']

ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_FORMS = {'signup': 'sign.forms.CommonSignupForm'}
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = 'agata.vandaik@yandex.ru'

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_BROKER_URL')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_BEAT_SCHEDULE = {
    'weekly_newsletter_8am': {
        'task': 'news.tasks.weekly_newsletter_task',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
    },
}
SITE_URL = 'http://127.0.0.1:8000'

#CACHES = {
    #'default':{
        #'BACKEND': 'django.core.cache.backends.redis.RedisCache',
       # 'LOCATION': 'redis://default:KXjYbU9nFEyYbJq6TiM1TCP6PpJTQcSJ@redis-18631.c73.us-east-1-2.ec2.cloud.redislabs.com:18631/0',
   # }
#}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'style': '{',
    'formatters': {
        # Формат для DEBUG (время, уровень, сообщение)
        'console_debug': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
        },
        # Формат для WARNING (добавляем путь pathname)
        'console_warning': {
            'format': '{asctime} {levelname} {message} {pathname}',
            'style': '{',
        },
        # Формат для ERROR/CRITICAL (добавляем стек exc_info)
        'console_error': {
            'format': '{asctime} {levelname} {message} {pathname} {exc_info}',
            'style': '{',
        },
        'general_format': {
            'format': '{asctime} {levelname} {module} {message}',
            'style': '{',
        },
        'error_format': {
            'format': '{asctime} {levelname} {message} {pathname} {exc_info}',
            'style': '{',
        },
        'email_format': {
            'format': '{asctime} {levelname} {message} {pathname}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        # Пункт 1: Три обработчика для консоли с разными форматами
        'console_debug_handler': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'console_debug'
        },
        'console_warning_handler': {
            'level': 'WARNING',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'console_warning'
        },
        'console_error_handler': {
            'level': 'ERROR',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'console_error'
        },
        # Пункт 2: general.log
        'general_file': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.FileHandler',
            'filename': 'general.log',
            'formatter': 'general_format',
        },
        # Пункт 3: errors.log
        'errors_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'errors.log',
            'formatter': 'error_format',
        },
        # Пункт 4: security.log
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'security.log',
            'formatter': 'general_format',
        },
        # Пункт 5: Почта
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'email_format',
        },
    },
    'loggers': {
        'django': {
            # Привязываем все консольные форматы + файл general
            'handlers': ['console_debug_handler', 'console_warning_handler', 'console_error_handler', 'general_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['errors_file', 'mail_admins'],
            'propagate': True,
        },
        'django.server': {
            'handlers': ['errors_file', 'mail_admins'],
            'propagate': True,
        },
        'django.template': {
            'handlers': ['errors_file'],
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['errors_file'],
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file'],
            'propagate': True,
        },
    }
}
ADMINS = [
    ('Agata', 'agata.vandaik@yandex.ru'),
]

# Чтобы Django понимал, от кого приходят письма:
SERVER_EMAIL = 'agata.vandaik@yandex.ru'
