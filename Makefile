# Project Makefile
#
# A generic makefile for projects.
#
# https://github.com/project-makefile/project-makefile

# --------------------------------------------------------------------------------
# Variables (override)
# --------------------------------------------------------------------------------

.DEFAULT_GOAL := git-commit-push

UNAME := $(shell uname)
RANDIR := $(shell openssl rand -base64 12 | sed 's/\///g')
TMPDIR := $(shell mktemp -d)

PROJECT_EMAIL := aclark@aclark.net
PROJECT_MAKEFILE := project.mk
PROJECT_NAME = project-makefile
PROJECT_DIRS = backend contactpage home privacy siteuser

WAGTAIL_CLEAN_DIRS = home search backend sitepage siteuser privacy frontend contactpage modelformtest
WAGTAIL_CLEAN_FILES = README.rst .dockerignore Dockerfile manage.py requirements.txt

REVIEW_EDITOR = subl

GIT_BRANCHES = $(shell git branch -a | grep remote | grep -v HEAD | grep -v main |\
    grep -v master)
GIT_MESSAGE = "Update $(PROJECT_NAME)"
GIT_COMMIT = git commit -a -m $(GIT_MESSAGE)
GIT_PUSH = git push
GIT_PUSH_FORCE = git push --force-with-lease

GET_DATABASE_URL = eb ssh -c "source /opt/elasticbeanstalk/deployment/custom_env_var;\
    env | grep DATABASE_URL"
DATABASE_AWK = awk -F\= '{print $$2}'
DATABASE_HOST = $(shell $(GET_DATABASE_URL) | $(DATABASE_AWK) |\
    python -c 'import dj_database_url; url = input(); url = dj_database_url.parse(url); print(url["HOST"])')
DATABASE_NAME = $(shell $(GET_DATABASE_URL) | $(DATABASE_AWK) |\
    python -c 'import dj_database_url; url = input(); url = dj_database_url.parse(url); print(url["NAME"])')
DATABASE_PASS = $(shell $(GET_DATABASE_URL) | $(DATABASE_AWK) |\
    python -c 'import dj_database_url; url = input(); url = dj_database_url.parse(url); print(url["PASSWORD"])')
DATABASE_USER = $(shell $(GET_DATABASE_URL) | $(DATABASE_AWK) |\
    python -c 'import dj_database_url; url = input(); url = dj_database_url.parse(url); print(url["USER"])')

ENV_NAME ?= $(PROJECT_NAME)-$(GIT_BRANCH)-$(GIT_REV)
INSTANCE_MAX ?= 1
INSTANCE_MIN ?= 1
INSTANCE_TYPE ?= t4g.small
INSTANCE_PROFILE ?= aws-elasticbeanstalk-ec2-role
PLATFORM ?= "Python 3.11 running on 64bit Amazon Linux 2023"
LB_TYPE ?= application

ifneq ($(wildcard $(PROJECT_MAKEFILE)),)
    include $(PROJECT_MAKEFILE)
endif

# --------------------------------------------------------------------------------
# Variables (no override)
# --------------------------------------------------------------------------------

GIT_REV := $(shell git rev-parse --short HEAD)
GIT_BRANCH := $(shell git branch --show-current)

ADD_DIR := mkdir -pv
ADD_FILE := touch
COPY_DIR := cp -rv
COPY_FILE := cp -v
DEL_DIR := rm -rv
DEL_FILE := rm -v
GIT_ADD := -git add

ENSURE_PIP := python -m ensurepip

# --------------------------------------------------------------------------------
# Multi-line variables
# --------------------------------------------------------------------------------

define ALLAUTH_LAYOUT_BASE
{% extends 'base.html' %}
endef

define AUTHENTICATION_BACKENDS
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
endef

define BABELRC
{
  "presets": [
    [
      "@babel/preset-react",
    ],
    [
      "@babel/preset-env",
      {
        "useBuiltIns": "usage",
        "corejs": "3.0.0"
      }
    ]
  ],
  "plugins": [
    "@babel/plugin-syntax-dynamic-import",
    "@babel/plugin-transform-class-properties"
  ]
}
endef

define BASE_TEMPLATE
{% load static wagtailcore_tags wagtailuserbar webpack_loader %}

<!DOCTYPE html>
<html lang="en" class="h-100" data-bs-theme="{{ request.user.user_theme_preference|default:'light' }}">
    <head>
        <meta charset="utf-8" />
        <title>
            {% block title %}
            {% if page.seo_title %}{{ page.seo_title }}{% else %}{{ page.title }}{% endif %}
            {% endblock %}
            {% block title_suffix %}
            {% wagtail_site as current_site %}
            {% if current_site and current_site.site_name %}- {{ current_site.site_name }}{% endif %}
            {% endblock %}
        </title>
        {% if page.search_description %}
        <meta name="description" content="{{ page.search_description }}" />
        {% endif %}
        <meta name="viewport" content="width=device-width, initial-scale=1" />

        {# Force all links in the live preview panel to be opened in a new tab #}
        {% if request.in_preview_panel %}
        <base target="_blank">
        {% endif %}

        {% stylesheet_pack 'app' %}

        {% block extra_css %}
        {# Override this in templates to add extra stylesheets #}
        {% endblock %}

        <style>
          .success {
              background-color: #d4edda;
              border-color: #c3e6cb;
              color: #155724;
          }
          .info {
              background-color: #d1ecf1;
              border-color: #bee5eb;
              color: #0c5460;
          }
          .warning {
              background-color: #fff3cd;
              border-color: #ffeeba;
              color: #856404;
          }
          .danger {
              background-color: #f8d7da;
              border-color: #f5c6cb;
              color: #721c24;
          }
        </style>
        {% include 'favicon.html' %}
        {% csrf_token %}
    </head>
    <body class="{% block body_class %}{% endblock %} d-flex flex-column h-100">
        <main class="flex-shrink-0">
            {% wagtailuserbar %}
            <div id="app"></div>
            {% include 'header.html' %}
            {% if messages %}
                <div class="messages container">
                    {% for message in messages %}
                        <div class="alert {{ message.tags }} alert-dismissible fade show"
                             role="alert">
                            {{ message }}
                            <button type="button"
                                    class="btn-close"
                                    data-bs-dismiss="alert"
                                    aria-label="Close"></button>
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
            <div class="container">
                {% block content %}{% endblock %}
            </div>
        </main>
        {% include 'footer.html' %}
        {% include 'offcanvas.html' %}
        {% javascript_pack 'app' %}
        {% block extra_js %}
        {# Override this in templates to add extra javascript #}
        {% endblock %}
    </body>
</html>
endef


define BLOCK_CAROUSEL
        <div id="carouselExampleCaptions" class="carousel slide">
            <div class="carousel-indicators">
                {% for image in block.value.images %}
                    <button type="button"
                            data-bs-target="#carouselExampleCaptions"
                            data-bs-slide-to="{{ forloop.counter0 }}"
                            {% if forloop.first %}class="active" aria-current="true"{% endif %}
                            aria-label="Slide {{ forloop.counter }}"></button>
                {% endfor %}
            </div>
            <div class="carousel-inner">
                {% for image in block.value.images %}
                    <div class="carousel-item {% if forloop.first %}active{% endif %}">
                        <img src="{{ image.file.url }}" class="d-block w-100" alt="...">
                        <div class="carousel-caption d-none d-md-block">
                            <h5>{{ image.title }}</h5>
                        </div>
                    </div>
                {% endfor %}
            </div>
            <button class="carousel-control-prev"
                    type="button"
                    data-bs-target="#carouselExampleCaptions"
                    data-bs-slide="prev">
                <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                <span class="visually-hidden">Previous</span>
            </button>
            <button class="carousel-control-next"
                    type="button"
                    data-bs-target="#carouselExampleCaptions"
                    data-bs-slide="next">
                <span class="carousel-control-next-icon" aria-hidden="true"></span>
                <span class="visually-hidden">Next</span>
            </button>
        </div>
endef

define BLOCK_MARKETING
{% load wagtailcore_tags %}
<div class="{{ self.block_class }}">
    {% if block.value.images.0 %}
        {% include 'blocks/carousel_block.html' %}
    {% else %}
        {{ self.title }}
        {{ self.content }}
    {% endif %}
</div>
endef

define CONTACT_PAGE_TEST
from wagtail.models import Page, Site
from wagtail.rich_text import RichText
from wagtail.test.utils import WagtailPageTestCase

from home.models import HomePage
from contactpage.models import ContactPage 


class ContactPageTest(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        root = Page.get_first_root_node()
        Site.objects.create(
            hostname="testserver",
            root_page=root,
            is_default_site=True,
            site_name="testserver",
        )
        home = HomePage(title="Home")
        root.add_child(instance=home)
        cls.page = ContactPage(
            title="Contact Us",
            slug="contact-us",
        )
        home.add_child(instance=cls.page)

    def test_get(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
endef

define COMPONENT_CLOCK
// Via ChatGPT
import React, { useState, useEffect, useCallback, useRef } from 'react';
import PropTypes from 'prop-types';

const Clock = ({ color = '#fff' }) => {
  const [date, setDate] = useState(new Date());
  const [blink, setBlink] = useState(true);
  const timerID = useRef();

  const tick = useCallback(() => {
    setDate(new Date());
    setBlink(prevBlink => !prevBlink);
  }, []);

  useEffect(() => {
    timerID.current = setInterval(() => tick(), 1000);

    // Return a cleanup function to be run on component unmount
    return () => clearInterval(timerID.current);
  }, [tick]);

  const formattedDate = date.toLocaleDateString(undefined, {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  const formattedTime = date.toLocaleTimeString(undefined, {
    hour: 'numeric',
    minute: 'numeric',
  });

  return (
    <> 
      <div style={{ animation: blink ? 'blink 1s infinite' : 'none' }}><span className='me-2'>{formattedDate}</span> {formattedTime}</div>
    </>
  );
};

Clock.propTypes = {
  color: PropTypes.string,
};

export default Clock;
endef

define COMPONENT_ERROR
import { Component } from 'react';
import PropTypes from 'prop-types';

class ErrorBoundary extends Component {
  constructor (props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError () {
    return { hasError: true };
  }

  componentDidCatch (error, info) {
    const { onError } = this.props;
    console.error(error);
    onError && onError(error, info);
  }

  render () {
    const { children = null } = this.props;
    const { hasError } = this.state;

    return hasError ? null : children;
  }
}

ErrorBoundary.propTypes = {
  onError: PropTypes.func,
  children: PropTypes.node,
};

export default ErrorBoundary;
endef

define COMPONENT_USER_MENU
// UserMenu.js
import React from 'react';
import PropTypes from 'prop-types';

function handleLogout() {
    window.location.href = '/accounts/logout';
}

const UserMenu = ({ isAuthenticated, isSuperuser, textColor }) => {
  return (
    <div> 
      {isAuthenticated ? (
        <li className="nav-item dropdown">
          <a className="nav-link dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
              <i className="fa-solid fa-circle-user"></i>
          </a>
          <ul className="dropdown-menu">
            <li><a className="dropdown-item" href="/user/profile">Profile</a></li>
            <li><a className="dropdown-item" href="/modelformtest/test-models">Model Form Test</a></li>
            {isSuperuser ? (
              <>
                <li><hr className="dropdown-divider"></hr></li>
                <li><a className="dropdown-item" href="/django" target="_blank">Django admin</a></li>
                <li><a className="dropdown-item" href="/wagtail" target="_blank">Wagtail admin</a></li>
                <li><a className="dropdown-item" href="/api" target="_blank">Django REST framework</a></li>
              </>
            ) : null}
            <li><hr className="dropdown-divider"></hr></li>
            <li><a className="dropdown-item" href="/accounts/logout">Logout</a></li>
          </ul>
        </li>
      ) : (
        <li className="nav-item">
          <a className={`nav-link text-$${textColor}`} href="/accounts/login"><i className="fa-solid fa-circle-user"></i></a>
        </li>
      )}
    </div>
  );
};

UserMenu.propTypes = {
  isAuthenticated: PropTypes.bool.isRequired,
  isSuperuser: PropTypes.bool.isRequired,
  textColor: PropTypes.string,
};

export default UserMenu;
endef


define CONTACT_PAGE_TEMPLATE
{% extends 'base.html' %}
{% load crispy_forms_tags static wagtailcore_tags %}
{% block content %}
        <h1>{{ page.title }}</h1>
        {{ page.intro|richtext }}
        <form action="{% pageurl page %}" method="POST">
            {% csrf_token %}
            {{ form.as_p }}
            <input type="submit">
        </form>
{% endblock %}
endef

define CONTACT_PAGE_TEST
from django.test import TestCase
from wagtail.test.utils import WagtailPageTestCase
from wagtail.models import Page

from contactpage.models import ContactPage, FormField

class ContactPageTest(TestCase, WagtailPageTestCase):
    def test_contact_page_creation(self):
        # Create a ContactPage instance
        contact_page = ContactPage(
            title='Contact',
            intro='Welcome to our contact page!',
            thank_you_text='Thank you for reaching out.'
        )

        # Save the ContactPage instance
        self.assertEqual(contact_page.save_revision().publish().get_latest_revision_as_page(), contact_page)

    def test_form_field_creation(self):
        # Create a ContactPage instance
        contact_page = ContactPage(
            title='Contact',
            intro='Welcome to our contact page!',
            thank_you_text='Thank you for reaching out.'
        )
        # Save the ContactPage instance
        contact_page_revision = contact_page.save_revision()
        contact_page_revision.publish()

        # Create a FormField associated with the ContactPage
        form_field = FormField(
            page=contact_page,
            label='Your Name',
            field_type='singleline',
            required=True
        )
        form_field.save()

        # Retrieve the ContactPage from the database
        contact_page_from_db = Page.objects.get(id=contact_page.id).specific

        # Check if the FormField is associated with the ContactPage
        self.assertEqual(contact_page_from_db.form_fields.first(), form_field)

    def test_contact_page_form_submission(self):
        # Create a ContactPage instance
        contact_page = ContactPage(
            title='Contact',
            intro='Welcome to our contact page!',
            thank_you_text='Thank you for reaching out.'
        )
        # Save the ContactPage instance
        contact_page_revision = contact_page.save_revision()
        contact_page_revision.publish()

        # Simulate a form submission
        form_data = {
            'your_name': 'John Doe',
            # Add other form fields as needed
        }

        response = self.client.post(contact_page.url, form_data)

        # Check if the form submission is successful (assuming a 302 redirect)
        self.assertEqual(response.status_code, 302)
        
        # You may add more assertions based on your specific requirements
endef

define CONTACT_PAGE_MODEL
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel, FieldRowPanel,
    InlinePanel, MultiFieldPanel
)
from wagtail.fields import RichTextField
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField


class FormField(AbstractFormField):
    page = ParentalKey('ContactPage', on_delete=models.CASCADE, related_name='form_fields')


class ContactPage(AbstractEmailForm):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro'),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]

    class Meta:
        verbose_name = "Contact Page"
endef

define CONTACT_PAGE_LANDING
{% extends 'base.html' %}
{% block content %}<div class="container"><h1>Thank you!</h1></div>{% endblock %}
endef

define DOCKERFILE
FROM amazonlinux:2023
RUN dnf install -y shadow-utils python3.11 python3.11-pip make nodejs20-npm nodejs postgresql15 postgresql15-server
USER postgres
RUN initdb -D /var/lib/pgsql/data
USER root
RUN useradd wagtail
EXPOSE 8000
ENV PYTHONUNBUFFERED=1 PORT=8000
COPY requirements.txt /
RUN python3.11 -m pip install -r /requirements.txt
WORKDIR /app
RUN chown wagtail:wagtail /app
COPY --chown=wagtail:wagtail . .
USER wagtail
RUN cd frontend; npm-20 install; npm-20 run build
RUN python3.11 manage.py collectstatic --noinput --clear
CMD set -xe; pg_ctl -D /var/lib/pgsql/data -l /tmp/logfile start; python3.11 manage.py migrate --noinput; gunicorn backend.wsgi:application
endef

define DOCKERCOMPOSE
version: '3'

services:
  db:
    image: postgres:latest
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: project
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin

  web:
    build: .
    command: sh -c "python manage.py migrate && gunicorn project.wsgi:application -b 0.0.0.0:8000"
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgres://admin:admin@db:5432/project

volumes:
  postgres_data:
endef

define INTERNAL_IPS
INTERNAL_IPS = ["127.0.0.1",]
endef


define ESLINTRC
{
    "env": {
        "browser": true,
        "es2021": true,
        "node": true
    },
    "extends": [
        "eslint:recommended",
        "plugin:react/recommended"
    ],
    "overrides": [
        {
            "env": {
                "node": true
            },
            "files": [
                ".eslintrc.{js,cjs}"
            ],
            "parserOptions": {
                "sourceType": "script"
            }
        }
    ],
    "parserOptions": {
        "ecmaVersion": "latest",
        "sourceType": "module"
    },
    "plugins": [
        "react"
    ],
    "rules": {
        "no-unused-vars": "off"
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
}
endef

define FAVICON_TEMPLATE
{% load static %}
<link href="{% static 'wagtailadmin/images/favicon.ico' %}" rel="icon">
endef


define HOME_PAGE_MODEL
from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail_color_panel.fields import ColorField
from wagtail_color_panel.edit_handlers import NativeColorPanel


class MarketingBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, help_text='Enter the block title')
    content = blocks.RichTextBlock(required=False, help_text='Enter the block content')
    images = blocks.ListBlock(ImageChooserBlock(required=False), help_text="Select one or two images for column display. Select three or more images for carousel display.")
    image = ImageChooserBlock(required=False, help_text="Select one image for background display.")
    block_class = blocks.CharBlock(
        required=False,
        help_text='Enter a CSS class for styling the marketing block',
        classname='full title',
        default='vh-100 bg-secondary',
    )
    image_class = blocks.CharBlock(
        required=False,
        help_text='Enter a CSS class for styling the column display image(s)',
        classname='full title',
        default='img-thumbnail p-5',
    )
    layout_class = blocks.CharBlock(
        required=False,
        help_text='Enter a CSS class for styling the layout.',
        classname='full title',
        default='d-flex flex-row',
    )

    class Meta:
        icon = 'placeholder'
        template = 'blocks/marketing_block.html'


class HomePage(Page):
    template = 'home/home_page.html'  # Create a template for rendering the home page
    marketing_blocks = StreamField([
        ('marketing_block', MarketingBlock()),
    ], blank=True, null=True, use_json_field=True)
    content_panels = Page.content_panels + [
        FieldPanel('marketing_blocks'),
    ]

    class Meta:
        verbose_name = 'Home Page'
endef

define HOME_PAGE_TEMPLATE
{% extends "base.html" %}
{% load wagtailcore_tags %}
{% block content %}
    <main class="{% block main_class %}{% endblock %}">
        {% for block in page.marketing_blocks %}
           {% include_block block %}
        {% endfor %}
    </main>
{% endblock %}
endef

define INDEX_HTML
<h1>Hello world</h1>
endef

define JENKINS_FILE
pipeline {
    agent any
    stages {
        stage('') {
            steps {
                echo ''
            }
        }
    }
}
endef

define SITEPAGE_MODEL
from wagtail.models import Page


class SitePage(Page):
    template = "sitepage/site_page.html"

    class Meta:
        verbose_name = "Site Page"
endef

define SEARCH_TEMPLATE
{% extends "base.html" %}
{% load static wagtailcore_tags %}
{% block body_class %}template-searchresults{% endblock %}
{% block title %}Search{% endblock %}
{% block content %}
    <h1>Search</h1>
    <form action="{% url 'search' %}" method="get">
        <input type="text"
               name="query"
               {% if search_query %}value="{{ search_query }}"{% endif %}>
        <input type="submit" value="Search" class="button">
    </form>
    {% if search_results %}
        <ul>
            {% for result in search_results %}
                <li>
                    <h4>
                        <a href="{% pageurl result %}">{{ result }}</a>
                    </h4>
                    {% if result.search_description %}{{ result.search_description }}{% endif %}
                </li>
            {% endfor %}
        </ul>
        {% if search_results.has_previous %}
            <a href="{% url 'search' %}?query={{ search_query|urlencode }}&amp;page={{ search_results.previous_page_number }}">Previous</a>
        {% endif %}
        {% if search_results.has_next %}
            <a href="{% url 'search' %}?query={{ search_query|urlencode }}&amp;page={{ search_results.next_page_number }}">Next</a>
        {% endif %}
    {% elif search_query %}
        No results found
	{% else %}
		No results found. Try a <a href="?query=test">test query</a>?
    {% endif %}
{% endblock %}
endef

define SEARCH_URLS
from django.urls import path
from .views import search

urlpatterns = [
    path("", search, name="search")
]
endef

define SITEUSER_URLS
from django.urls import path
from .views import UserProfileView, UpdateThemePreferenceView, UserEditView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('update_theme_preference/', UpdateThemePreferenceView.as_view(), name='update_theme_preference'),
    path('<int:pk>/edit/', UserEditView.as_view(), name='user-edit'),
]
endef

define BACKEND_URLS
from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from rest_framework import routers, serializers, viewsets
# from dj_rest_auth.registration.views import RegisterView

from siteuser.models import User

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('django/', admin.site.urls),
    path('wagtail/', include(wagtailadmin_urls)),
    path('user/', include('siteuser.urls')),
    path('search/', include('search.urls')),
    path('modelformtest/', include('modelformtest.urls')),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

# https://www.django-rest-framework.org/#example
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns += [
    path("api/", include(router.urls)),
    path("api/", include("rest_framework.urls", namespace="rest_framework")),
    # path("api/", include("dj_rest_auth.urls")),
    # path("api/register/", RegisterView.as_view(), name="register"),
]

urlpatterns += [
    path("hijack/", include("hijack.urls")),
]

urlpatterns += [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),

    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
endef

define REST_FRAMEWORK
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}
endef

define FRONTEND_APP_CONFIG
import '../utils/themeToggler.js';
import '../utils/tinymce.js';
endef

define FRONTEND_PORTAL
// Via pwellever
import React from 'react';
import { createPortal } from 'react-dom';

const parseProps = data => Object.entries(data).reduce((result, [key, value]) => {
  if (value.toLowerCase() === 'true') {
    value = true;
  } else if (value.toLowerCase() === 'false') {
    value = false;
  } else if (value.toLowerCase() === 'null') {
    value = null;
  } else if (!isNaN(parseFloat(value)) && isFinite(value)) {
    // Parse numeric value
    value = parseFloat(value);
  } else if (
    (value[0] === '[' && value.slice(-1) === ']') || (value[0] === '{' && value.slice(-1) === '}')
  ) {
    // Parse JSON strings
    value = JSON.parse(value);
  }

  result[key] = value;
  return result;
}, {});

// This method of using portals instead of calling ReactDOM.render on individual components
// ensures that all components are mounted under a single React tree, and are therefore able
// to share context.

export default function getPageComponents (components) {
  const getPortalComponent = domEl => {
    // The element's "data-component" attribute is used to determine which component to render.
    // All other "data-*" attributes are passed as props.
    const { component: componentName, ...rest } = domEl.dataset;
    const Component = components[componentName];
    if (!Component) {
      console.error(`Component "$${componentName}" not found.`);
      return null;
    }
    const props = parseProps(rest);
    domEl.innerHTML = '';

    // eslint-disable-next-line no-unused-vars
    const { ErrorBoundary } = components;
    return createPortal(
      <ErrorBoundary>
        <Component {...props} />
      </ErrorBoundary>,
      domEl,
    );
  };

  return Array.from(document.querySelectorAll('[data-component]')).map(getPortalComponent);
}
endef

define FRONTEND_COMPONENTS
export { default as ErrorBoundary } from './ErrorBoundary';
export { default as UserMenu } from './UserMenu';
endef

define FRONTEND_CONTEXT_INDEX
export { UserContextProvider as default } from './UserContextProvider';
endef

define FRONTEND_CONTEXT_USER_PROVIDER
// UserContextProvider.js
import React, { createContext, useContext, useState } from 'react';
import PropTypes from 'prop-types';

const UserContext = createContext();

export const UserContextProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const login = () => {
    try {
      // Add logic to handle login, set isAuthenticated to true
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Login error:', error);
      // Handle error, e.g., show an error message to the user
    }
  };

  const logout = () => {
    try {
      // Add logic to handle logout, set isAuthenticated to false
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
      // Handle error, e.g., show an error message to the user
    }
  };

  return (
    <UserContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </UserContext.Provider>
  );
};

UserContextProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export const useUserContext = () => {
  const context = useContext(UserContext);

  if (!context) {
    throw new Error('useUserContext must be used within a UserContextProvider');
  }

  return context;
};

// Add PropTypes for the return value of useUserContext
useUserContext.propTypes = {
  isAuthenticated: PropTypes.bool.isRequired,
  login: PropTypes.func.isRequired,
  logout: PropTypes.func.isRequired,
};
endef

define FRONTEND_STYLES
// If you comment out code below, bootstrap will use red as primary color
// and btn-primary will become red

// $primary: red;

@import "~bootstrap/scss/bootstrap.scss";

.jumbotron {
  // should be relative path of the entry scss file
  background-image: url("../../vendors/images/sample.jpg");
  background-size: cover;
}

#theme-toggler-authenticated:hover {
    cursor: pointer; /* Change cursor to pointer on hover */
    color: #007bff; /* Change color on hover */
}

#theme-toggler-anonymous:hover {
    cursor: pointer; /* Change cursor to pointer on hover */
    color: #007bff; /* Change color on hover */
}
endef

define FRONTEND_APP
import React from 'react';
import { createRoot } from 'react-dom/client';
import 'bootstrap';
import '@fortawesome/fontawesome-free/js/fontawesome';
import '@fortawesome/fontawesome-free/js/solid';
import '@fortawesome/fontawesome-free/js/regular';
import '@fortawesome/fontawesome-free/js/brands';
import getDataComponents from '../dataComponents';
import UserContextProvider from '../context';
import * as components from '../components';
import "../styles/index.scss";
import "../styles/theme-blue.scss";
import "./config";

const { ErrorBoundary } = components;
const dataComponents = getDataComponents(components);
const container = document.getElementById('app');
const root = createRoot(container);
const App = () => (
    <ErrorBoundary>
      <UserContextProvider>
        {dataComponents}
      </UserContextProvider>
    </ErrorBoundary>
)
root.render(<App />);
endef

define GIT_IGNORE
__pycache__
*.pyc
dist/
node_modules/
_build/
.elasticbeanstalk/
endef

define HTML_FOOTER
{% load wagtailcore_tags %}
  <footer class="footer mt-auto py-3 bg-body-tertiary pt-5 text-center text-small">
    {% wagtail_site as current_site %}
    <p class="mb-1">&copy; {% now "Y" %} {{ current_site.site_name|default:"Project Makefile" }}</p>
    <ul class="list-inline">
      <li class="list-inline-item"><a class="text-secondary text-decoration-none {% if request.path == '/' %}active{% endif %}" href="/">Home</a></li>
      {% for child in current_site.root_page.get_children %}
          <li class="list-inline-item"><a class="text-secondary text-decoration-none {% if request.path == child.url %}active{% endif %}" href="{{ child.url }}">{{ child }}</a></li>
      {% endfor %}
    </ul>
  </footer>
endef


define HTML_HEADER
{% load wagtailcore_tags %}
{% wagtail_site as current_site %}
<div class="app-header">
    <div class="container py-4 app-navbar">
        <nav class="navbar navbar-transparent navbar-padded navbar-expand-md">
            <a class="navbar-brand me-auto" href="/">{{ current_site.site_name|default:"Project Makefile" }}</a>
            <button class="navbar-toggler"
                    type="button"
                    data-bs-toggle="offcanvas"
                    data-bs-target="#offcanvasExample"
                    aria-controls="offcanvasExample"
                    aria-expanded="false"
                    aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="d-none d-md-block">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a id="home-nav"
                           class="nav-link {% if request.path == '/' %}active{% endif %}"
                           aria-current="page"
                           href="/">Home</a>
                    </li>
                    {% for child in current_site.root_page.get_children %}
                        {% if child.show_in_menus %}
                            <li class="nav-item">
                                <a class="nav-link {% if request.path == child.url %}active{% endif %}" aria-current="page"
                                    href="{{ child.url }}">{{ child }}</a>
                            </li>
                        {% endif %}
                    {% endfor %}
                    <div data-component="UserMenu"
                         data-is-authenticated="{{ request.user.is_authenticated }}"
                         data-is-superuser="{{ request.user.is_superuser }}"></div>
                    <li class="nav-item" id="{% if request.user.is_authenticated %}theme-toggler-authenticated{% else %}theme-toggler-anonymous{% endif %}">
                        <span class="nav-link" data-bs-toggle="tooltip" title="Toggle dark mode">
                            <i class="fas fa-circle-half-stroke"></i>
                        </span>
                    </li>
                    <li class="nav-item">
                        <form class="form" action="{% url 'search' %}">
                            <div class="row">
                                <div class="col-8">
                                    <input class="form-control"
                                           type="search"
                                           name="query"
                                           {% if search_query %}value="{{ search_query }}"{% endif %}>
                                </div>
                                <div class="col-4">
                                    <input type="submit" value="Search" class="form-control">
                                </div>
                            </div>
                        </form>
                    </li>
                </ul>
            </div>
        </nav>
    </div>
</div>
endef 

define HTML_OFFCANVAS
{% load wagtailcore_tags %}
{% wagtail_site as current_site %}
<div class="offcanvas offcanvas-start bg-dark" tabindex="-1" id="offcanvasExample" aria-labelledby="offcanvasExampleLabel">
  <div class="offcanvas-header">
    <a class="offcanvas-title text-light h5 text-decoration-none" id="offcanvasExampleLabel" href="/">{{ current_site.site_name|default:"Project Makefile" }}</a>
    <button type="button" class="btn-close bg-light" data-bs-dismiss="offcanvas" aria-label="Close"></button>
  </div>
  <div class="offcanvas-body bg-dark">
    {% wagtail_site as current_site %}
    <ul class="navbar-nav justify-content-end flex-grow-1 pe-3">
      <li class="nav-item">
        <a class="nav-link text-light active" aria-current="page" href="/">Home</a>
      </li>
      {% for child in current_site.root_page.get_children %}
      <li class="nav-item">
        <a class="nav-link text-light" href="{{ child.url }}">{{ child }}</a>
      </li>
      {% endfor %}
      <li class="nav-item" id="{% if request.user.is_authenticated %}theme-toggler-authenticated{% else %}theme-toggler-anonymous{% endif %}">
          <span class="nav-link text-light" data-bs-toggle="tooltip" title="Toggle dark mode">
              <i class="fas fa-circle-half-stroke"></i>
          </span>
      </li>
      <div data-component="UserMenu" data-text-color="light" data-is-authenticated="{{ request.user.is_authenticated }}" data-is-superuser="{{ request.user.is_superuser }}"></div>
    </ul>
  </div>
</div>
endef

define MODEL_FORM_TEST_MODEL
from django.db import models
from django.shortcuts import reverse

class TestModel(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"test-model-{self.pk}"

    def get_absolute_url(self):
        return reverse('test_model_detail', kwargs={'pk': self.pk})
endef

define MODEL_FORM_TEST_ADMIN
from django.contrib import admin
from .models import TestModel

@admin.register(TestModel)
class TestModelAdmin(admin.ModelAdmin):
    pass
endef

define MODEL_FORM_TEST_VIEWS
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from .models import TestModel
from .forms import TestModelForm


class TestModelListView(ListView):
    model = TestModel
    template_name = "test_model_list.html"
    context_object_name = "test_models"


class TestModelCreateView(CreateView):
    model = TestModel
    form_class = TestModelForm
    template_name = "test_model_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class TestModelUpdateView(UpdateView):
    model = TestModel
    form_class = TestModelForm
    template_name = "test_model_form.html"


class TestModelDetailView(DetailView):
    model = TestModel
    template_name = "test_model_detail.html"
    context_object_name = "test_model"
endef

define MODEL_FORM_TEST_FORMS
from django import forms
from .models import TestModel

class TestModelForm(forms.ModelForm):
    class Meta:
        model = TestModel
        fields = ['name', 'email', 'age', 'is_active']  # Add or remove fields as needed
endef

define MODEL_FORM_TEST_TEMPLATE_FORM
{% extends 'base.html' %}
{% block content %}
    <h1>{% if form.instance.pk %}Update Test Model{% else %}Create Test Model{% endif %}</h1>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Save</button>
    </form>
{% endblock %}
endef

define MODEL_FORM_TEST_TEMPLATE_DETAIL
{% extends 'base.html' %}
{% block content %}
    <h1>Test Model Detail: {{ test_model.name }}</h1>
    <p>Name: {{ test_model.name }}</p>
    <p>Email: {{ test_model.email }}</p>
    <p>Age: {{ test_model.age }}</p>
    <p>Active: {{ test_model.is_active }}</p>
    <p>Created At: {{ test_model.created_at }}</p>
    <a href="{% url 'test_model_update' test_model.pk %}">Edit Test Model</a>
{% endblock %}
endef

define MODEL_FORM_TEST_TEMPLATE_LIST
{% extends 'base.html' %}
{% block content %}
    <h1>Test Models List</h1>
    <ul>
        {% for test_model in test_models %}
            <li><a href="{% url 'test_model_detail' test_model.pk %}">{{ test_model.name }}</a></li>
        {% endfor %}
    </ul>
    <a href="{% url 'test_model_create' %}">Create New Test Model</a>
{% endblock %}
endef

define MODEL_FORM_TEST_URLS
from django.urls import path
from .views import (
    TestModelListView,
    TestModelCreateView,
    TestModelUpdateView,
    TestModelDetailView,
)

urlpatterns = [
    path('test-models/', TestModelListView.as_view(), name='test_model_list'),
    path('test-models/create/', TestModelCreateView.as_view(), name='test_model_create'),
    path('test-models/<int:pk>/update/', TestModelUpdateView.as_view(), name='test_model_update'),
    path('test-models/<int:pk>/', TestModelDetailView.as_view(), name='test_model_detail'),
]
endef

define PRIVACY_PAGE_MODEL
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtailmarkdown.fields import MarkdownField


class PrivacyPage(Page):
    """
    A Wagtail Page model for the Privacy Policy page.
    """

    template = "privacy_page.html"

    body = MarkdownField()

    content_panels = Page.content_panels + [
        FieldPanel("body", classname="full"),
    ]

    class Meta:
        verbose_name = "Privacy Page"
endef

define PRIVACY_PAGE_TEMPLATE
{% extends 'base.html' %}
{% load wagtailmarkdown %}
{% block content %}<div class="container">{{ page.body|markdown }}</div>{% endblock %}
endef

define REQUIREMENTS_TEST
pytest
pytest-runner
coverage
pytest-mock
pytest-cov
hypothesis
selenium
pytest-django
factory-boy
flake8
tox
endef

define SITEUSER_FORM
from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import User

class SiteUserForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ("username", "user_theme_preference", "bio", "rate")

    bio = forms.CharField(widget=forms.Textarea(attrs={"id": "editor"}), required=False)
endef

define SITEUSER_MODEL
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings

class User(AbstractUser):
    groups = models.ManyToManyField(Group, related_name='siteuser_set', blank=True)
    user_permissions = models.ManyToManyField(
        Permission, related_name='siteuser_set', blank=True
    )
    
    user_theme_preference = models.CharField(max_length=10, choices=settings.THEMES, default='light')
    
    bio = models.TextField(blank=True, null=True)
    rate = models.FloatField(blank=True, null=True)
endef

define SETTINGS_THEMES
THEMES = [
    ('light', 'Light Theme'),
    ('dark', 'Dark Theme'),
]
endef

define SITEUSER_ADMIN
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from .models import User

admin.site.register(User, UserAdmin)
endef

define SITEUSER_EDIT_TEMPLATE
{% extends 'base.html' %}

{% block content %}
  <h2>Edit User</h2>
  <form method="post">
    {% csrf_token %}
    {{ form }}
    <div class="d-flex">
      <button type="submit">Save changes</button>
      <a class="text-decoration-none" href="/user/profile">Cancel</a>
    </div>
  </form>
{% endblock %}
endef

define SITEUSER_VIEW_TEMPLATE
{% extends 'base.html' %}

{% block content %}
<h2>User Profile</h2>
<div class="d-flex justify-content-end">
    <a class="btn btn-outline-secondary" href="{% url 'user-edit' pk=user.id %}">Edit</a>
</div>
<p>Username: {{ user.username }}</p>
<p>Theme: {{ user.user_theme_preference }}</p>
<p>Bio: {{ user.bio|default:""|safe }}</p>
<p>Rate: {{ user.rate|default:"" }}</p>
{% endblock %}
endef

define SITEUSER_VIEW
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from .models import User
from .forms import SiteUserForm


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "profile.html"

    def get_object(self, queryset=None):
        return self.request.user


@method_decorator(csrf_exempt, name="dispatch")
class UpdateThemePreferenceView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode("utf-8"))
            new_theme = data.get("theme")
            user = request.user
            user.user_theme_preference = new_theme
            user.save()
            response_data = {"theme": new_theme}
            return JsonResponse(response_data)
        except json.JSONDecodeError as e:
            return JsonResponse({"error": e}, status=400)

    def http_method_not_allowed(self, request, *args, **kwargs):
        return JsonResponse({"error": "Invalid request method"}, status=405)


class UserEditView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'user_edit.html'  # Create this template in your templates folder
    form_class = SiteUserForm

    def get_success_url(self):
        # return reverse_lazy('user-profile', kwargs={'pk': self.object.pk})
        return reverse_lazy('user-profile')
endef

define SITEPAGE_TEMPLATE
{% extends 'base.html' %}
{% block content %}
    <h1>{{ page.title }}</h1>
{% endblock %}
endef

define THEME_BLUE
@import "~bootstrap/scss/bootstrap.scss";

[data-bs-theme="blue"] {
  --bs-body-color: var(--bs-white);
  --bs-body-color-rgb: #{to-rgb($$white)};
  --bs-body-bg: var(--bs-blue);
  --bs-body-bg-rgb: #{to-rgb($$blue)};
  --bs-tertiary-bg: #{$$blue-600};

  .dropdown-menu {
    --bs-dropdown-bg: #{color-mix($$blue-500, $$blue-600)};
    --bs-dropdown-link-active-bg: #{$$blue-700};
  }

  .btn-secondary {
    --bs-btn-bg: #{color-mix($gray-600, $blue-400, .5)};
    --bs-btn-border-color: #{rgba($$white, .25)};
    --bs-btn-hover-bg: #{color-adjust(color-mix($gray-600, $blue-400, .5), 5%)};
    --bs-btn-hover-border-color: #{rgba($$white, .25)};
    --bs-btn-active-bg: #{color-adjust(color-mix($gray-600, $blue-400, .5), 10%)};
    --bs-btn-active-border-color: #{rgba($$white, .5)};
    --bs-btn-focus-border-color: #{rgba($$white, .5)};

    // --bs-btn-focus-box-shadow: 0 0 0 .25rem rgba(255, 255, 255, 20%);
  }
}
endef

define THEME_TOGGLER
document.addEventListener('DOMContentLoaded', function () {
    const rootElement = document.documentElement;
    const anonThemeToggle = document.getElementById('theme-toggler-anonymous');
    const authThemeToggle = document.getElementById('theme-toggler-authenticated');
    if (authThemeToggle) {
        localStorage.removeItem('data-bs-theme');
    }
    const anonSavedTheme = localStorage.getItem('data-bs-theme');
    if (anonSavedTheme) {
        rootElement.setAttribute('data-bs-theme', anonSavedTheme);
    }
    if (anonThemeToggle) {
        anonThemeToggle.addEventListener('click', function () {
            const currentTheme = rootElement.getAttribute('data-bs-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            rootElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('data-bs-theme', newTheme);
        });
    }
    if (authThemeToggle) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        authThemeToggle.addEventListener('click', function () {
            const currentTheme = rootElement.getAttribute('data-bs-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            fetch('/user/update_theme_preference/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken, // Include the CSRF token in the headers
                },
                body: JSON.stringify({ theme: newTheme }),
            })
            .then(response => response.json())
            .then(data => {
                rootElement.setAttribute('data-bs-theme', newTheme);
            })
            .catch(error => {
                console.error('Error updating theme preference:', error);
            });
        });
    }
});
endef

define TINYMCE_JS
import tinymce from 'tinymce';
import 'tinymce/icons/default';
import 'tinymce/themes/silver';
import 'tinymce/skins/ui/oxide/skin.css';
import 'tinymce/plugins/advlist';
import 'tinymce/plugins/code';
import 'tinymce/plugins/emoticons';
import 'tinymce/plugins/emoticons/js/emojis';
import 'tinymce/plugins/link';
import 'tinymce/plugins/lists';
import 'tinymce/plugins/table';
import 'tinymce/models/dom';

tinymce.init({
  selector: 'textarea#editor',
  plugins: 'advlist code emoticons link lists table',
  toolbar: 'bold italic | bullist numlist | link emoticons',
  skin: false,
  content_css: false,
});
endef

define WEBPACK_CONFIG_JS
const path = require('path');

module.exports = {
  mode: 'development',
  entry: './src/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
  },
};
endef

define WEBPACK_REVEAL_CONFIG_JS
const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  mode: 'development',
  entry: './src/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
  },
  module: {
    rules: [
      {
        test: /\.css$$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader'],
      },
    ],
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: 'bundle.css',
    }),
  ],
};
endef

define WEBPACK_INDEX_HTML
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hello, Webpack!</title>
</head>
<body>
  <script src="dist/bundle.js"></script>
</body>
</html>
endef

define WEBPACK_REVEAL_INDEX_HTML
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Project Makefile</title>
        <link rel="stylesheet" href="dist/bundle.css">
    </head>
    <div class="reveal">
        <div class="slides">
            <section>
                Slide 1: Draw some circles
            </section>
            <section>
                Slide 2: Draw the rest of the owl
            </section>
        </div>
    </div>
    <script src="dist/bundle.js"></script>
</html>
endef

define WEBPACK_INDEX_JS
const message = "Hello, World!";
console.log(message);
endef

define WEBPACK_REVEAL_INDEX_JS
import 'reveal.js/dist/reveal.css';
import 'reveal.js/dist/theme/black.css';
import Reveal from 'reveal.js';
import RevealNotes from 'reveal.js/plugin/notes/notes.js';
Reveal.initialize({ slideNumber: true, plugins: [ RevealNotes ]});
endef

# ------------------------------------------------------------------------------  
# Export variables
# ------------------------------------------------------------------------------  

export ALLAUTH_LAYOUT_BASE
export AUTHENTICATION_BACKENDS
export BABELRC
export BACKEND_URLS
export BASE_TEMPLATE
export BLOCK_CAROUSEL
export BLOCK_MARKETING
export COMPONENT_CLOCK
export COMPONENT_ERROR
export COMPONENT_USER_MENU
export CONTACT_PAGE_MODEL
export CONTACT_PAGE_TEMPLATE
export CONTACT_PAGE_LANDING
export CONTACT_PAGE_TEST
export DOCKERFILE
export DOCKERCOMPOSE
export ESLINTRC
export FAVICON_TEMPLATE
export FRONTEND_APP
export FRONTEND_APP_CONFIG
export FRONTEND_COMPONENTS
export FRONTEND_PORTAL
export FRONTEND_STYLES
export GIT_IGNORE
export HOME_PAGE_MODEL
export HOME_PAGE_TEMPLATE
export HTML_FOOTER
export HTML_HEADER
export HTML_OFFCANVAS
export INDEX_HTML
export INTERNAL_IPS
export JENKINS_FILE
export MODEL_FORM_TEST_ADMIN
export MODEL_FORM_TEST_FORMS
export MODEL_FORM_TEST_MODEL
export MODEL_FORM_TEST_URLS
export MODEL_FORM_TEST_VIEWS
export MODEL_FORM_TEST_TEMPLATE_DETAIL
export MODEL_FORM_TEST_TEMPLATE_FORM
export MODEL_FORM_TEST_TEMPLATE_LIST
export PRIVACY_PAGE_MODEL
export REST_FRAMEWORK
export FRONTEND_CONTEXT_INDEX
export FRONTEND_CONTEXT_USER_PROVIDER
export PRIVACY_PAGE_MODEL
export PRIVACY_PAGE_TEMPLATE
export REQUIREMENTS_TEST
export SETTINGS_THEMES
export SITEPAGE_MODEL
export SITEPAGE_TEMPLATE
export SITEUSER_FORM
export SITEUSER_MODEL
export SITEUSER_ADMIN
export SITEUSER_URLS
export SITEUSER_VIEW
export SITEUSER_VIEW_TEMPLATE
export SITEUSER_EDIT_TEMPLATE
export SEARCH_TEMPLATE
export SEARCH_URLS
export THEME_BLUE
export THEME_TOGGLER
export TINYMCE_JS
export WEBPACK_CONFIG_JS
export WEBPACK_INDEX_HTML
export WEBPACK_INDEX_JS
export WEBPACK_REVEAL_CONFIG_JS
export WEBPACK_REVEAL_INDEX_HTML
export WEBPACK_REVEAL_INDEX_JS

# ------------------------------------------------------------------------------  
# Rules
# ------------------------------------------------------------------------------  

aws-ssm-describe-parameters-default:
	@aws ssm describe-parameters | cat

aws-ssm-default:
ifdef AWS_PROFILE
	@echo "Environment variable is set: $(AWS_PROFILE)"
	aws ssm describe-parameters | cat
	@echo "Get parameter values with: aws ssm getparameter --name <Name>."
else
	@echo "Environment variable not set. Set AWS_PROFILE before running this target."
endif

docker-build-default:
	podman build -t $(PROJECT_NAME) .

docker-compose-default:
	podman compose up

docker-serve-default:
	podman run -p 8000:8000 $(PROJECT_NAME)

eb-check-env-default:  # https://stackoverflow.com/a/4731504/185820
ifndef SSH_KEY
	$(error SSH_KEY is undefined)
endif
ifndef VPC_ID
	$(error VPC_ID is undefined)
endif
ifndef VPC_SG
	$(error VPC_SG is undefined)
endif
ifndef VPC_SUBNET_EC2
	$(error VPC_SUBNET_EC2 is undefined)
endif
ifndef VPC_SUBNET_ELB
	$(error VPC_SUBNET_ELB is undefined)
endif

eb-create-default: eb-check-env
	eb create $(ENV_NAME) \
         -im $(INSTANCE_MIN) \
         -ix $(INSTANCE_MAX) \
         -ip $(INSTANCE_PROFILE) \
         -i $(INSTANCE_TYPE) \
         -k $(SSH_KEY) \
         -p $(PLATFORM) \
         --elb-type $(LB_TYPE) \
         --vpc \
         --vpc.id $(VPC_ID) \
         --vpc.elbpublic \
         --vpc.publicip \
         --vpc.ec2subnets $(VPC_SUBNET_EC2) \
         --vpc.elbsubnets $(VPC_SUBNET_ELB) \
         --vpc.securitygroups $(VPC_SG)

eb-deploy-default:
	eb deploy

eb-restart-default:
	eb ssh -c "systemctl restart web"

eb-upgrade-default:
	eb upgrade

eb-init-default:
	eb init

eb-list-platforms-default:
	aws elasticbeanstalk list-platform-versions

eb-list-databases-default:
	@eb ssh --quiet -c "export PGPASSWORD=$(DATABASE_PASS); psql -l -U $(DATABASE_USER) -h $(DATABASE_HOST) $(DATABASE_NAME)"

eb-logs-default:
	eb logs

eb-secret-default:
	@SECRET_KEY=$$(openssl rand -base64 48); \
    aws ssm put-parameter --name "SECRET_KEY" --value "$$SECRET_KEY" --type String

npm-init-default:
	npm init -y
	$(GIT_ADD) package.json
	-$(GIT_ADD) package-lock.json

npm-build-default:
	npm run build

npm-install-default:
	npm install
	$(GIT_ADD) package-lock.json

npm-clean-default:
	$(DEL_DIR) dist/
	$(DEL_DIR) node_modules/
	$(DEL_FILE) package-lock.json

npm-serve-default:
	npm run start

db-mysql-init-default:
	-mysqladmin -u root drop $(PROJECT_NAME)
	-mysqladmin -u root create $(PROJECT_NAME)

db-pg-init-default:
	-dropdb $(PROJECT_NAME)
	-createdb $(PROJECT_NAME)

db-pg-init-test-default:
	-dropdb test_$(PROJECT_NAME)
	-createdb test_$(PROJECT_NAME)

db-pg-export-default:
	@eb ssh --quiet -c "export PGPASSWORD=$(DATABASE_PASS); pg_dump -U $(DATABASE_USER) -h $(DATABASE_HOST) $(DATABASE_NAME)" > $(DATABASE_NAME).sql
	@echo "Wrote $(DATABASE_NAME).sql"

db-pg-import-default:
	@psql $(DATABASE_NAME) < $(DATABASE_NAME).sql

django-frontend-app-default: python-webpack-init
	$(ADD_DIR) frontend/src/context
	$(ADD_DIR) frontend/src/images
	$(ADD_DIR) frontend/src/utils
	@echo "$$COMPONENT_CLOCK" > frontend/src/components/Clock.js
	@echo "$$COMPONENT_ERROR" > frontend/src/components/ErrorBoundary.js
	@echo "$$FRONTEND_CONTEXT_INDEX" > frontend/src/context/index.js
	@echo "$$FRONTEND_CONTEXT_USER_PROVIDER" > frontend/src/context/UserContextProvider.js
	@echo "$$COMPONENT_USER_MENU" > frontend/src/components/UserMenu.js
	@echo "$$FRONTEND_APP" > frontend/src/application/app.js
	@echo "$$FRONTEND_APP_CONFIG" > frontend/src/application/config.js
	@echo "$$FRONTEND_COMPONENTS" > frontend/src/components/index.js
	@echo "$$FRONTEND_PORTAL" > frontend/src/dataComponents.js
	@echo "$$FRONTEND_STYLES" > frontend/src/styles/index.scss
	@echo "$$BABELRC" > frontend/.babelrc
	@echo "$$ESLINTRC" > frontend/.eslintrc
	@echo "$$THEME_BLUE" > frontend/src/styles/theme-blue.scss
	@echo "$$THEME_TOGGLER" > frontend/src/utils/themeToggler.js
	@echo "$$TINYMCE_JS" > frontend/src/utils/tinymce.js
	-$(GIT_ADD) home
	-$(GIT_ADD) frontend

django-secret-default:
	@python -c "from secrets import token_urlsafe; print(token_urlsafe(50))"

django-siteuser-default:
	python manage.py startapp siteuser
	@echo "$$SITEUSER_FORM" > siteuser/forms.py
	@echo "$$SITEUSER_MODEL" > siteuser/models.py
	@echo "$$SITEUSER_ADMIN" > siteuser/admin.py
	@echo "$$SITEUSER_VIEW" > siteuser/views.py
	@echo "$$SITEUSER_URLS" > siteuser/urls.py
	$(ADD_DIR) siteuser/templates/
	$(ADD_DIR) siteuser/management/commands
	@echo "$$SITEUSER_VIEW_TEMPLATE" > siteuser/templates/profile.html
	@echo "$$SITEUSER_EDIT_TEMPLATE" > siteuser/templates/user_edit.html
	@echo "INSTALLED_APPS.append('siteuser')" >> $(SETTINGS)
	@echo "AUTH_USER_MODEL = 'siteuser.User'" >> $(SETTINGS)
	python manage.py makemigrations siteuser
	$(GIT_ADD) siteuser/

django-graph-default:
	python manage.py graph_models -a -o $(PROJECT_NAME).png

django-show-urls-default:
	python manage.py show_urls

django-loaddata-default:
	python manage.py loaddata

django-migrate-default:
	python manage.py migrate

django-migrations-default:
	python manage.py makemigrations

django-migrations-show-default:
	python manage.py showmigrations

django-model-form-test-default:
	python manage.py startapp modelformtest
	@echo "$$MODEL_FORM_TEST_ADMIN" > modelformtest/admin.py
	@echo "$$MODEL_FORM_TEST_FORMS" > modelformtest/forms.py
	@echo "$$MODEL_FORM_TEST_MODEL" > modelformtest/models.py
	@echo "$$MODEL_FORM_TEST_URLS" > modelformtest/urls.py
	@echo "$$MODEL_FORM_TEST_VIEWS" > modelformtest/views.py
	$(ADD_DIR) modelformtest/templates/modelformtest
	@echo "$$MODEL_FORM_TEST_TEMPLATE_DETAIL" > modelformtest/templates/test_model_detail.html
	@echo "$$MODEL_FORM_TEST_TEMPLATE_FORM" > modelformtest/templates/test_model_form.html
	@echo "$$MODEL_FORM_TEST_TEMPLATE_LIST" > modelformtest/templates/modelformtest/testmodel_list.html
	@echo "INSTALLED_APPS.append('modelformtest')" >> $(SETTINGS)
	python manage.py makemigrations
	$(GIT_ADD) modelformtest

django-serve-default:
	cd frontend; npm run watch &
	python manage.py runserver 0.0.0.0:8000

django-settings-default:
	echo "# $(PROJECT_NAME)" >> $(SETTINGS)
	echo "ALLOWED_HOSTS = ['*']" >> $(SETTINGS)
	echo "import dj_database_url  # noqa" >> $(SETTINGS)
	echo "DATABASE_URL = os.environ.get('DATABASE_URL', \
         'postgres://$(DB_USER):$(DB_PASS)@$(DB_HOST):$(DB_PORT)/$(PROJECT_NAME)')" >> $(SETTINGS)
	echo "DATABASES['default'] = dj_database_url.parse(DATABASE_URL)" >> $(SETTINGS)
	echo "INSTALLED_APPS.append('webpack_boilerplate')" >> $(SETTINGS)
	echo "INSTALLED_APPS.append('rest_framework')" >> $(SETTINGS)
	echo "INSTALLED_APPS.append('rest_framework.authtoken')" >> $(SETTINGS)
	echo "INSTALLED_APPS.append('allauth')" >> $(SETTINGS)
	echo "INSTALLED_APPS.append('allauth.account')" >> $(SETTINGS)
	echo "INSTALLED_APPS.append('allauth.socialaccount')" >> $(SETTINGS)
	echo "INSTALLED_APPS.append('wagtailmenus')" >> $(SETTINGS)
	echo "INSTALLED_APPS.append('wagtailmarkdown')" >> $(SETTINGS)
	echo "INSTALLED_APPS.append('wagtail_modeladmin')" >> $(SETTINGS)
	echo "INSTALLED_APPS.append('wagtailseo')" >> $(SETTINGS)
	echo "INSTALLED_APPS.append('wagtail_color_panel')" >> $(SETTINGS)
	echo "INSTALLED_APPS.append('wagtail.contrib.settings')" >> $(SETTINGS)
	echo "INSTALLED_APPS.append('django_extensions')" >> $(SETTINGS)
	echo "INSTALLED_APPS.append('debug_toolbar')" >> $(DEV_SETTINGS)
	echo "INSTALLED_APPS.append('crispy_forms')" >> $(SETTINGS)
	echo "INSTALLED_APPS.append('crispy_bootstrap5')" >> $(SETTINGS)
	echo "INSTALLED_APPS.append('django_recaptcha')" >> $(SETTINGS)
	echo "MIDDLEWARE.append('allauth.account.middleware.AccountMiddleware')" >> $(SETTINGS)
	echo "MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')" >> $(DEV_SETTINGS)
	echo "MIDDLEWARE.append('hijack.middleware.HijackUserMiddleware')" >> $(DEV_SETTINGS)
	echo "STATICFILES_DIRS.append(os.path.join(BASE_DIR, 'frontend/build'))" >> $(SETTINGS)
	echo "WEBPACK_LOADER = { 'MANIFEST_FILE': os.path.join(BASE_DIR, 'frontend/build/manifest.json'), }" >> $(SETTINGS)
	echo "$$REST_FRAMEWORK" >> $(SETTINGS)
	echo "$$SETTINGS_THEMES" >> $(SETTINGS)
	echo "$$INTERNAL_IPS" >> $(DEV_SETTINGS)
	echo "LOGIN_REDIRECT_URL = '/'" >> $(SETTINGS)
	echo "DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'" >> $(SETTINGS)
	echo "$$AUTHENTICATION_BACKENDS" >> $(SETTINGS)
	echo "TEMPLATES[0]['OPTIONS']['context_processors'].append('wagtail.contrib.settings.context_processors.settings')" >> $(SETTINGS)
	echo "TEMPLATES[0]['OPTIONS']['context_processors'].append('wagtailmenus.context_processors.wagtailmenus')">> $(SETTINGS)
	echo "SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']" >> $(SETTINGS)

django-crispy-default:
	@echo "CRISPY_TEMPLATE_PACK = 'bootstrap5'" >> $(SETTINGS)
	@echo "CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'" >> $(SETTINGS)

django-shell-default:
	python manage.py shell

django-static-default:
	python manage.py collectstatic --noinput

django-su-default:
	DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --noinput --username=admin --email=$(PROJECT_EMAIL)

django-test-default: django-npm-install django-npm-build django-static
	-$(MAKE) pip-install-test
	python manage.py test

django-user-default:
	python manage.py shell -c "from django.contrib.auth.models import User; \
        User.objects.create_user('user', '', 'user')"

django-url-patterns-default:
	echo "$$BACKEND_URLS" > backend/$(URLS)

django-npm-install-default:
	cd frontend; npm install

django-npm-install-save-default:
	cd frontend; npm install \
        @fortawesome/fontawesome-free \
        @fortawesome/fontawesome-svg-core \
        @fortawesome/free-brands-svg-icons \
        @fortawesome/free-solid-svg-icons \
        @fortawesome/react-fontawesome \
        camelize \
        date-fns \
        history \
        mapbox-gl \
        query-string \
        react-animate-height \
        react-chartjs-2 \
        react-copy-to-clipboard \
        react-date-range \
        react-dom \
        react-dropzone \
        react-hook-form \
        react-image-crop \
        react-map-gl \
        react-modal \
        react-resize-detector \
        react-select \
        react-swipeable \
        snakeize \
        striptags \
        tinymce \
        url-join \
        viewport-mercator-project

django-npm-install-save-dev-default:
	cd frontend; npm install \
        eslint-plugin-react \
        eslint-config-standard \
        eslint-config-standard-jsx \
        @babel/core \
        @babel/preset-env \
        @babel/preset-react \
        --save-dev

django-npm-test-default:
	cd frontend; npm run test

django-npm-build-default:
	cd frontend; npm run build

django-open-default:
ifeq ($(UNAME), Linux)
	@echo "Opening on Linux."
	xdg-open http://0.0.0.0:8000
else ifeq ($(UNAME), Darwin)
	@echo "Opening on macOS (Darwin)."
	open http://0.0.0.0:8000
else
	@echo "Unable to open on: $(UNAME)"
endif

favicon-default:
	dd if=/dev/urandom bs=64 count=1 status=none | base64 | convert -size 16x16 -depth 8 -background none -fill white label:@- favicon.png
	convert favicon.png favicon.ico
	$(GIT_ADD) favicon.ico
	$(DEL_FILE) favicon.png

gh-default:
	gh browse

git-ignore-default:
	echo "$$GIT_IGNORE" > .gitignore
	$(GIT_ADD) .gitignore

git-branches-default:
	-for i in $(GIT_BRANCHES) ; do \
        git checkout -t $$i ; done

git-commit-default:
	-@$(GIT_COMMIT)

git-push-default:
	-@$(GIT_PUSH)

git-push-force-default:
	-@$(GIT_PUSH_FORCE)

git-commit-edit-default:
	-git commit -a

git-prune-default:
	git remote update origin --prune

git-set-upstream-default:
	git push --set-upstream origin main

git-commit-empty-default:
	git commit --allow-empty -m "Empty-Commit"

help-default:
	@for makefile in $(MAKEFILE_LIST); do \
        $(MAKE) -pRrq -f $$makefile : 2>/dev/null \
            | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' \
            | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' \
            | xargs | tr ' ' '\n' \
            | awk '{printf "%s\n", $$0}' ; done | less # http://stackoverflow.com/a/26339924

index-default:
	@echo "$$INDEX_HTML" > index.html

jenkins-init-default:
	@echo "$$JENKINS_FILE" > Jenkinsfile

lint-default:
	-ruff check -v --fix
	-ruff format -v
	-djlint --reformat --format-css --format-js .

make-default:
	$(GIT_ADD) Makefile
	-git commit Makefile -m "Add/update project-makefile files"
	-git push

pip-freeze-default:
	$(ENSURE_PIP)
	python -m pip freeze | sort > $(TMPDIR)/requirements.txt
	mv -f $(TMPDIR)/requirements.txt .
	$(GIT_ADD) requirements.txt

pip-init-default:
	touch requirements.txt
	$(GIT_ADD) requirements.txt

pip-init-test-default:
	@echo "$$REQUIREMENTS_TEST" > requirements-test.txt
	$(GIT_ADD) requirements-test.txt

pip-install-default:
	$(ENSURE_PIP)
	$(MAKE) pip-upgrade
	python -m pip install wheel
	python -m pip install -r requirements.txt

pip-install-dev-default:
	$(ENSURE_PIP)
	python -m pip install -r requirements-dev.txt

pip-install-test-default:
	$(ENSURE_PIP)
	python -m pip install -r requirements-test.txt

pip-install-upgrade-default:
	cat requirements.txt | awk -F\= '{print $$1}' > $(TMPDIR)/requirements.txt
	mv -f $(TMPDIR)/requirements.txt .
	$(ENSURE_PIP)
	python -m pip install -U -r requirements.txt
	python -m pip freeze | sort > $(TMPDIR)/requirements.txt
	mv -f $(TMPDIR)/requirements.txt .

pip-upgrade-default:
	$(ENSURE_PIP)
	python -m pip install -U pip

pip-uninstall-default:
	$(ENSURE_PIP)
	python -m pip freeze | xargs python -m pip uninstall -y

project-mk-default:
	touch project.mk
	$(GIT_ADD) project.mk

python-serve-default:
	@echo "\n\tServing HTTP on http://0.0.0.0:8000\n"
	python3 -m http.server

python-setup-sdist-default:
	python3 setup.py sdist --format=zip

python-webpack-init-default:
	python manage.py webpack_init --no-input

rand-default:
	@openssl rand -base64 12 | sed 's/\///g'

readme-init-rst-default:
	@echo "$(PROJECT_NAME)" > README.rst
	@echo "================================================================================" >> README.rst
	-@git add README.rst

readme-init-md-default:
	@echo "# $(PROJECT_NAME)" > README.md
	-@git add README.md

readme-edit-rst-default:
	vi README.rst

readme-edit-md-default:
	vi README.md

readme-open-default:
	open README.pdf

readme-build-default:
	rst2pdf README.rst

reveal-build-default:
	npm run build

reveal-init-default: webpack-reveal-init
	npm install \
       css-loader \
       mini-css-extract-plugin \
       reveal.js \
       style-loader
	jq '.scripts += {"build": "webpack"}' package.json > \
        $(TMPDIR)/tmp.json && mv $(TMPDIR)/tmp.json package.json
	jq '.scripts += {"start": "webpack serve --mode development --port 8000 --static"}' package.json > \
        $(TMPDIR)/tmp.json && mv $(TMPDIR)/tmp.json package.json
	jq '.scripts += {"watch": "webpack watch --mode development"}' package.json > \
        $(TMPDIR)/tmp.json && mv $(TMPDIR)/tmp.json package.json

reveal-serve-default:
	npm run watch &
	python -m http.server

sphinx-init-default: sphinx-install
	sphinx-quickstart -q -p $(PROJECT_NAME) -a $(USER) -v 0.0.1 $(RANDIR)
	$(COPY_DIR) $(RANDIR)/* .
	$(DEL_DIR) $(RANDIR)
	$(GIT_ADD) index.rst
	$(GIT_ADD) conf.py
	$(DEL_FILE) make.bat
	git checkout Makefile
	$(MAKE) gitignore

sphinx-theme-init-default:
	export THEME_NAME=$(PROJECT_NAME)_theme; \
	$(ADD_DIR) $$THEME_NAME ; \
	$(ADD_FILE) $$THEME_NAME/__init__.py ; \
	$(GIT_ADD) $$THEME_NAME/__init__.py ; \
	$(ADD_FILE) $$THEME_NAME/theme.conf ; \
	$(GIT_ADD) $$THEME_NAME/theme.conf ; \
	$(ADD_FILE) $$THEME_NAME/layout.html ; \
	$(GIT_ADD) $$THEME_NAME/layout.html ; \
	$(ADD_DIR) $$THEME_NAME/static/css ; \
	$(ADD_FILE) $$THEME_NAME/static/css/style.css ; \
	$(ADD_DIR) $$THEME_NAME/static/js ; \
	$(ADD_FILE) $$THEME_NAME/static/js/script.js ; \
	$(GIT_ADD) $$THEME_NAME/static

review-default:
ifeq ($(UNAME), Darwin)
	$(REVIEW_EDITOR) `find backend/ -name \*.py` `find backend/ -name \*.html` `find frontend/ -name \*.js` `find frontend/ -name \*.js`
else
	@echo "Unsupported"
endif

sphinx-install-default:
	echo "Sphinx\n" > requirements.txt
	@$(MAKE) pip-install
	@$(MAKE) pip-freeze
	-$(GIT_ADD) requirements.txt

sphinx-build-default:
	sphinx-build -b html -d _build/doctrees . _build/html

sphinx-build-pdf-default:
	sphinx-build -b rinoh . _build/rinoh

sphinx-serve-default:
	cd _build/html;python3 -m http.server

usage-default:
	@echo "Project Makefile 🤷"
	@echo "Usage: make [options] [target] ..."
	@echo "Examples:"
	@echo "   make help    Print all targets"
	@echo "   make usage   Print this message"

wagtail-search-urls:
	@echo "$$SEARCH_URLS" > search/urls.py
	$(GIT_ADD) search

wagtail-search-template:
	@echo "$$SEARCH_TEMPLATE" > search/templates/search/search.html

wagtail-privacy-default:
	python manage.py startapp privacy
	@echo "$$PRIVACY_PAGE_MODEL" > privacy/models.py
	$(ADD_DIR) privacy/templates
	@echo "$$PRIVACY_PAGE_TEMPLATE" > privacy/templates/privacy_page.html
	@echo "INSTALLED_APPS.append('privacy')" >> $(SETTINGS)
	python manage.py makemigrations privacy
	$(GIT_ADD) privacy/

wagtail-base-default:
	@echo "$$BASE_TEMPLATE" > backend/templates/base.html

wagtail-header-default:
	@echo "$$HTML_HEADER" > backend/templates/header.html

wagtail-clean-default:
	-@for dir in "$(WAGTAIL_CLEAN_DIRS)"; do \
		$(DEL_DIR) $$dir; \
	done
	-@for file in "$(WAGTAIL_CLEAN_FILES)"; do \
		$(DEL_FILE) $$file; \
	done

wagtail-homepage-default:
	@echo "$$HOME_PAGE_MODEL" > home/models.py
	@echo "$$HOME_PAGE_TEMPLATE" > home/templates/home/home_page.html
	$(ADD_DIR) home/templates/blocks
	@echo "$$BLOCK_MARKETING" > home/templates/blocks/marketing_block.html
	@echo "$$BLOCK_CAROUSEL" > home/templates/blocks/carousel_block.html
	-$(GIT_ADD) home

wagtail-backend-templates-default:
	$(ADD_DIR) backend/templates/allauth/layouts
	@echo "$$ALLAUTH_LAYOUT_BASE" > backend/templates/allauth/layouts/base.html
	@echo "$$BASE_TEMPLATE" > backend/templates/base.html
	@echo "$$FAVICON_TEMPLATE" > backend/templates/favicon.html
	@echo "$$HTML_HEADER" > backend/templates/header.html
	@echo "$$HTML_FOOTER" > backend/templates/footer.html
	@echo "$$HTML_OFFCANVAS" > backend/templates/offcanvas.html
	$(GIT_ADD) backend/templates/

wagtail-start-default:
	wagtail start backend .

wagtail-init-default: db-init wagtail-install wagtail-start
	@echo "$$DOCKERFILE" > Dockerfile
	@echo "$$DOCKERCOMPOSE" > docker-compose.yml
	export SETTINGS=backend/settings/base.py DEV_SETTINGS=backend/settings/dev.py; \
		$(MAKE) django-settings
	export SETTINGS=backend/settings/base.py; \
		$(MAKE) django-model-form-test
	export URLS=urls.py; \
		$(MAKE) django-url-patterns
	$(GIT_ADD) backend
	$(GIT_ADD) requirements.txt
	$(GIT_ADD) manage.py
	$(GIT_ADD) Dockerfile
	$(GIT_ADD) .dockerignore
	$(MAKE) wagtail-homepage
	$(MAKE) wagtail-search-template
	$(MAKE) wagtail-search-urls
	export SETTINGS=backend/settings/base.py; \
		$(MAKE) django-siteuser
	export SETTINGS=backend/settings/base.py; \
		$(MAKE) wagtail-privacy
	export SETTINGS=backend/settings/base.py; \
		$(MAKE) wagtail-contactpage
	export SETTINGS=backend/settings/base.py; \
		$(MAKE) wagtail-sitepage
	export SETTINGS=backend/settings/base.py; \
		$(MAKE) django-crispy
	$(MAKE) django-migrations
	$(MAKE) django-migrate
	$(MAKE) su
	$(MAKE) wagtail-backend-templates
	@$(MAKE) django-frontend-app
	@$(MAKE) django-npm-install
	@$(MAKE) django-npm-install-save
	@$(MAKE) django-npm-install-save-dev
	@$(MAKE) pip-init-test
	@$(MAKE) readme
	@$(MAKE) gitignore
	@$(MAKE) freeze
	@$(MAKE) serve

wagtail-install-default:
	$(ENSURE_PIP)
	python -m pip install \
        Faker \
        boto3 \
        crispy-bootstrap5 \
        djangorestframework \
        django-allauth \
        django-after-response \
        django-ckeditor \
        django-colorful \
        django-cors-headers \
        django-countries \
        django-crispy-forms \
        django-debug-toolbar \
        django-extensions \
        django-hijack \
        django-honeypot \
        django-imagekit \
        django-import-export \
        django-ipware \
        django-multiselectfield \
        django-phonenumber-field \
        django-recurrence \
        django-recaptcha \
        django-registration \
        django-richtextfield \
        django-sendgrid-v5 \
        django-social-share \
        django-storages \
        django-tables2 \
        django-timezone-field \
		django-widget-tweaks \
        dj-database-url \
        dj-stripe \
        enmerkar \
        gunicorn \
        html2docx \
        icalendar \
        mailchimp-marketing \
        mailchimp-transactional \
        phonenumbers \
        psycopg2-binary \
        python-webpack-boilerplate \
        python-docx \
        reportlab \
        texttable \
        wagtail \
        wagtailmenus \
        wagtail-color-panel \
        wagtail-django-recaptcha \
        wagtail-markdown \
        wagtail_modeladmin \
        wagtail-seo \
        weasyprint \
        whitenoise \
        xhtml2pdf

webpack-init-default: npm-init
	@echo "$$WEBPACK_CONFIG_JS" > webpack.config.js
	$(GIT_ADD) webpack.config.js
	npm install --save-dev webpack webpack-cli webpack-dev-server
	$(ADD_DIR) src/
	@echo "$$WEBPACK_INDEX_JS" > src/index.js
	$(GIT_ADD) src/index.js
	@echo "$$WEBPACK_INDEX_HTML" > index.html
	$(GIT_ADD) index.html
	$(MAKE) gitignore

webpack-reveal-init-default: npm-init
	@echo "$$WEBPACK_REVEAL_CONFIG_JS" > webpack.config.js
	$(GIT_ADD) webpack.config.js
	npm install --save-dev webpack webpack-cli webpack-dev-server
	$(ADD_DIR) src/
	@echo "$$WEBPACK_REVEAL_INDEX_JS" > src/index.js
	$(GIT_ADD) src/index.js
	@echo "$$WEBPACK_REVEAL_INDEX_HTML" > index.html
	$(GIT_ADD) index.html
	$(MAKE) gitignore

wagtail-contactpage-default:
	python manage.py startapp contactpage
	@echo "$$CONTACT_PAGE_MODEL" > contactpage/models.py
	@echo "$$CONTACT_PAGE_TEST" > contactpage/tests.py
	$(ADD_DIR) contactpage/templates/contactpage/
	@echo "$$CONTACT_PAGE_TEMPLATE" > contactpage/templates/contactpage/contact_page.html
	@echo "$$CONTACT_PAGE_LANDING" > contactpage/templates/contactpage/contact_page_landing.html
	@echo "INSTALLED_APPS.append('contactpage')" >> $(SETTINGS)
	python manage.py makemigrations contactpage
	$(GIT_ADD) contactpage/

wagtail-sitepage-default:
	python manage.py startapp sitepage
	@echo "$$SITEPAGE_MODEL" > sitepage/models.py
	$(ADD_DIR) sitepage/templates/sitepage/
	@echo "$$SITEPAGE_TEMPLATE" > sitepage/templates/sitepage/site_page.html
	@echo "INSTALLED_APPS.append('sitepage')" >> $(SETTINGS)
	python manage.py makemigrations sitepage
	$(GIT_ADD) sitepage/

# ------------------------------------------------------------------------------  
# More rules
# ------------------------------------------------------------------------------  

b-default: build
build-default: pip-install
c-default: clean
ce-default: git-commit-edit-push
clean-default: wagtail-clean
cp-default: git-commit-push
d-default: deploy
db-export-default: db-pg-export
db-import-default: db-pg-import
db-init-default: db-pg-init
db-init-test-default: db-pg-init-test
deploy-default: eb-deploy
django-clean-default: wagtail-clean
django-init-default: wagtail-init
djlint-default: lint-djlint
e-default: edit
edit-default: readme-edit-md
empty-default: git-commit-empty
force-push-default: git-push-force
freeze-default: pip-freeze
git-commit-edit-push-default: git-commit-edit git-push
git-commit-push-default: git-commit git-push
gitignore-default: git-ignore
h-default: help
i-default: install
init-default: wagtail-init
install-default: pip-install
install-dev-default: pip-install-dev
install-test-default: pip-install-test
l-default: lint
logs-default: eb-logs
migrate-default: django-migrate
migrations-default: django-migrations
migrations-show-default: django-migrations-show
mk-default: project-mk
o-default: open
open-default: django-open
p-default: git-push
pack-default: django-npm-build
readme-default: readme-init-md
restart-default: eb-restart
reveal-default: reveal-init
s-default: serve
sdist-default: python-setup-sdist
secret-default: django-secret
serve-default: django-serve
shell-default: django-shell
show-urls-default: django-show-urls
ssm-list-default: aws-ssm-describe-parameters
static-default: django-static
su-default: django-su
test-default: django-test
u-default: usage
up-default: eb-upgrade
urls-default: django-show-urls
webpack-default: webpack-init

# --------------------------------------------------------------------------------
# Overrides
# --------------------------------------------------------------------------------

%: %-default  # https://stackoverflow.com/a/49804748
	@ true
