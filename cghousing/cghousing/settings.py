"""Django settings for the CGHousing (cghousing) project.

- For more information on this file, see
  https://docs.djangoproject.com/en/1.6/topics/settings/

- For the full list of settings and their values, see
  https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('CG_SECRET_KEY',
                       '8)qgord%ou9+0r)_#73+rGvqaaab8a662j$!&qsu2q7+fh%2r11(rw9')

CG_DEPLOY_TYPE = os.getenv('CG_DEPLOY_TYPE', 'prod')
DEBUG = False  # SECURITY WARNING: don't run with debug turned on in production!
TEMPLATE_DEBUG = False
if CG_DEPLOY_TYPE == 'dev':
    DEBUG = True
    TEMPLATE_DEBUG = True

# See https://docs.djangoproject.com/en/1.6/intro/tutorial02/#customizing-your-project-s-templates
TEMPLATE_DIRS = [
    os.path.join(BASE_DIR, 'templates'),
    os.path.join(BASE_DIR, 'templates/coop'),
]


ALLOWED_HOSTS = []
CG_ALLOWED_HOSTS = os.getenv('CG_ALLOWED_HOSTS')
if CG_ALLOWED_HOSTS:
    ALLOWED_HOSTS = [s.strip() for s in CG_ALLOWED_HOSTS.split(',')]

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'markdown_deux',
    'coop'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'cghousing.urls'

WSGI_APPLICATION = 'cghousing.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'prod': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('CG_DB_NAME', 'cghousing'),
        'USER': os.getenv('CG_DB_USER', 'cghousing'),
        'PASSWORD': os.getenv('CG_DB_PASSWORD', 'choose-a-better-password-a.}uBcZed?gz'),
        'HOST': os.getenv('CG_DB_HOST', ''),
        'PORT': os.getenv('CG_DB_PORT', ''),
    },
    'dev': {
         'ENGINE': 'django.db.backends.sqlite3',
         'NAME': os.path.join(BASE_DIR, 'coop.sqlite3'),
    }}
DATABASES['default'] = DATABASES.get(CG_DEPLOY_TYPE, DATABASES['dev'])


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.getenv('CG_TIME_ZONE', 'UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.getenv('CG_STATIC_ROOT', '/static/')

# WARN: commented-out because this seems to be not necessary as of Django 1.7, see
# http://deathofagremmie.com/2014/05/24/retiring-get-profile-and-auth-profile-module/ and
# https://docs.djangoproject.com/en/1.7/topics/auth/customizing/#extending-the-existing-user-model
# AUTH_PROFILE_MODULE = 'accounts.Person'

MARKDOWN_DEUX_STYLES = {
    "trusted": {
        "extras": {
            "code-friendly": None,
        },
        "safe_mode": False,
    },
    "default": {
        "extras": {
            "code-friendly": None,
        },
        "safe_mode": "escape",
    }
}

UPLOADS_PATH = os.getenv('CG_UPLOADS_PATH', '/uploads/')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'coop': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
