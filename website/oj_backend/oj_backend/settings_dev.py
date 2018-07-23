from oj_backend.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'potatooj_dev',
        'USER': 'yuan',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '',
    }
}
