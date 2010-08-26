# -*- coding: utf-8 -*-
DEBUG = {{ debug }}
STATIC_SERV = {{ static_serve }}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

SITE_HTTP = '{{ site_http }}'
