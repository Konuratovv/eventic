from decouple import config
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD', cast=int),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT', cast=int),
    }
}