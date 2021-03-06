# Django settings for nova project.
import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG
HOME = os.path.abspath(os.path.dirname(__file__)) 
WELCOME = True

ADMINS = (
    ('Bob Haugen', 'info@foodnetworksoftware.org'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'nova.sqlite'
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Halifax'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = HOME + "/media/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

ROOT_URLCONF = 'nova.urls'
LOGIN_URL = "/account/login"
LOGIN_REDIRECT_URLNAME = "no_permissions"

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(HOME, "templates/"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django_extensions',
    'django.contrib.humanize',
    'django.contrib.comments',
    'threadedcomments',
    'distribution',
    'customer',
    'producer',
    'notification',
    'mailer',
    'django.contrib.flatpages',
    'django.contrib.admin',
    'paypal.standard.ipn',
    'pay',
    'south',
    'easy_thumbnails',
)

THUMBNAIL_DEBUG = True

COMMENTS_APP = 'threadedcomments'

PAYPAL_RECEIVER_EMAIL = "bobha_1286809456_biz@gmail.com"
PAYPAL_IMAGE = "https://www.paypalobjects.com/WEBSCR-640-20101108-1/en_US/i/bnr/horizontal_solution_PP.gif"
PAYPAL_SANDBOX_IMAGE = "https://www.paypalobjects.com/WEBSCR-640-20101108-1/en_US/i/bnr/horizontal_solution_PP.gif"

COLOR_CHOICES = (
    ("#F0F8FF", 'Alice Blue'),
    ("#F0FFFF", 'Azure'),
    ("#F5F5DC", 'Beige'),
    ("#FFE4C4", 'Bisque'),
    ("#FFF8DC", 'Cornsilk'),
    ("#F0FFF0", 'Honeydew'),
    ("#CDFFCD", 'Light Sea Green'),
    ("#FFDEAD", 'Navajo White'),
    ('White', 'White'),
)

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass
