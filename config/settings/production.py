from decouple import config
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD', cast=int),
        'HOST': config('POSTGRES_HOST'),
        'PORT': config('POSTGRES_PORT', cast=int),
    }
}