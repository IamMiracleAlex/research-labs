from .base import *

import dj_database_url
import django_heroku

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ['research-labs.herokuapp.com']


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'research',
    }
}

MIDDLEWARE += [
    'whitenoise.middleware.WhiteNoiseMiddleware',
]





django_heroku.settings(locals())
