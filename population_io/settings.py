"""
Django settings for population_io project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('POPULATIONIO_SECRET_KEY', '0)c2!1m%#%fg1@k)mq&l5df9c8qdq_fh^25v%_s(*kg=ek*qk*')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('POPULATIONIO_DEBUG', 'true').lower() != 'false'

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['population.io', 'www.population.io', '104.130.5.217']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s] %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'api': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
    },
}
if 'test' in sys.argv:
    del LOGGING


# Application definition

INSTALLED_APPS = (
    'rest_framework',
    'corsheaders',
    'django.contrib.staticfiles',
    'api',
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',   # needs to come before CommonMiddleware
    'django.middleware.common.CommonMiddleware',
)

ROOT_URLCONF = 'population_io.urls'

WSGI_APPLICATION = 'population_io.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
# Here preconfigured for Heroku: https://devcenter.heroku.com/articles/getting-started-with-django#django-settings
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)


# REST Framework configuration
# http://www.django-rest-framework.org/api-guide/settings

# Setting up the API token authentication is done here via 1 Authentication and 2 Throttling classes:
# 'CustomTokenAuthentication' class is used if only requests with valid token should be allowed.
# 'TokenThrottle' is the main class for limiting the API usage per token as defined in the JSON file.
# 'PublicAccessThrottle' is optional class for limiting API usage in case public access is still allowed.
# Default throttling rate must be specified if 'PublicAccessThrottle' is used.

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('api.authentication.CustomTokenAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'DEFAULT_THROTTLE_CLASSES': (
        'api.throttling.TokenThrottle', 'api.throttling.PublicAccessThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1/min',
    },
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.JSONPRenderer',
    ),
}


# CORS headers configuration
# https://github.com/ottoyiu/django-cors-headers/#configuration

CORS_ORIGIN_ALLOW_ALL = True


# Settings of the api app

#DATA_STORE_PATH = os.environ.get('POPULATIONIO_DATASTORE_LOCATION', os.path.join(BASE_DIR, 'data', 'datastore.hdf5'))
DATA_STORE_PATH = os.environ.get('POPULATIONIO_DATASTORE_LOCATION', os.path.join(BASE_DIR, 'data'))
DATA_STORE_WRITABLE = os.environ.get('POPULATIONIO_DATASTORE_WRITABLE', 'true').lower() != 'false'
CSV_POPULATION_PATH = os.path.join(BASE_DIR, 'data', 'WPP2012_INT_F3_Population_By_Sex_Annual_Single_100_Medium.csv')
CSV_LIFE_EXPECTANCY_PATH = os.path.join(BASE_DIR, 'data', 'life_expectancy_ages.csv')
CSV_TOTAL_POPULATION_PATH = os.path.join(BASE_DIR, 'data', 'Total_population_for_date_and_countries_and_world.csv')
CSV_SURVIVAL_RATIO_PATH = os.path.join(BASE_DIR, 'data', 'Survival_ratio_Cohort_ages.csv')
CSV_CONTINENT_COUNTRIES = os.path.join(BASE_DIR, 'data', 'continent_countries.csv')
CSV_BIRTHS_DAY_COUNTRY = os.path.join(BASE_DIR, 'data', 'worldBirthsByDayAndCountry.csv')
JSON_API_TOKENS_PATH = os.path.join(BASE_DIR, 'data', 'api_keys.json')

CACHE_CONTROL_MAXAGE = 24 * 60 * 60
