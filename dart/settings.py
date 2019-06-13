# -*- coding: utf-8 -*-

# Copyright 2017 Lockheed Martin Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# SECURITY WARNING
# The settings here are intended for a quick, zero-hassle deployment.
# Since there's nothing quick and simple about production deployment,
# this is a great sign that these settings are not secure nor intended to be.
#
# Do NOT expose this application to an untrusted network.

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DART_VERSION_NUMBER = '2.1.0'

# SECURITY WARNING
# We are not randomizing this key for you.
SECRET_KEY = '5s9G+t##Trga48t594g1g8sret*(#*/rg-dfgs43wt)((dh/*d'

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',
    'bootstrap3',
    'base',
    'missions.apps.MissionsConfig',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'missions.middleware.RequiredInterstitial', # Uncomment and see related setting below if you require an interstitial
)

DEBUG=True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
		#Hard coding path for now. Try without this path or use Base_dir as described here; #https://stackoverflow.com/questions/3038459/django-template-path
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
				'missions.contextprocessors.context_processors.version_number',
            ],
			# SECURITY WARNING
			# We run in debug mode so that static files are automatically served
			# out by the built-in django webserver for ease of setup. Since you're already running
			# this on a trusted network (remember the security warning at the top of this file) you
			# are probably okay doing the same.
			'debug': DEBUG,
        },
    },
]

ROOT_URLCONF = 'dart.urls'

WSGI_APPLICATION = 'dart.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'supporting_data')
MEDIA_URL = '/data/'

# Bootstrap Settings
BOOTSTRAP3 = {
    'css_url': STATIC_URL + 'base/css/bootstrap.min.css',
    'javascript_url': STATIC_URL + 'base/js/bootstrap.min.js',
    'jquery_url': STATIC_URL + 'base/js/jquery.min.js',
    'required_css_class': 'required',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'maxBytes': 20000000,  # 20MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'info_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'info.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'missions': {
            'handlers': ['debug_file', 'info_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s [%(asctime)s] %(name)s: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
}

REPORT_TEMPLATE_PATH = os.path.join(BASE_DIR, '2016_Template.docx')


# Require an interstitial message to be displayed
#
# Some organizations may require an acceptable use policy or similar to be displayed upon logon,
# the setting REQUIRED_INTERSTITIAL_DISPLAY_INTERVAL will specify how often the AUP should be displayed
# in hours as a positive integer or 0 to indicate it should be displayed once per application logon.
# Omitting this setting will bypass the interstitial.
#
#REQUIRED_INTERSTITIAL_DISPLAY_INTERVAL = 0  # In hours, or 0 for once per login
