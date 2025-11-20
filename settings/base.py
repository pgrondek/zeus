# -*- coding: utf-8 -*-

import os
from django.utils.translation import gettext_lazy as _

# go through environment variables and override them


def get_from_env(var, default):
    if var in os.environ:
        return os.environ[var]
    else:
        return default


ROOT_PATH = os.path.join(os.path.dirname(__file__), '..')

# If deployment is set to anything else than `dev` we treat it as a production deployment
DEPLOYMENT = get_from_env('ZEUS_DEPLOYMENT','prod')
if DEPLOYMENT != 'dev':
    DEPLOYMENT = 'prod'

TESTING = False
DEBUG = False
ZEUS_TASK_DEBUG = False
CELERY_TASK_ALWAYS_EAGER = False
if DEPLOYMENT == 'dev':
    CELERY_TASK_ALWAYS_EAGER = True

ADMIN_NAME = get_from_env('ZEUS_ADMIN_NAME', 'Zeus admin')
ADMIN_EMAIL = get_from_env('ZEUS_ADMIN_EMAIL', 'zeus.admin@localhost')

ADMINS = [
    (ADMIN_NAME, ADMIN_EMAIL),
]

ELECTION_ADMINS = ADMINS
if 'ZEUS_ELECTION_ADMIN_NAME' in os.environ:
    ELECTION_ADMIN_NAME = get_from_env('ZEUS_ELECTION_ADMIN_NAME', 'Zeus election admin')
    ELECTION_ADMIN_EMAIL = get_from_env('ZEUS_ELECTION_ADMIN_EMAIL', 'zeus.election@localhost')

    ELECTION_ADMINS = [(ELECTION_ADMIN_NAME, ELECTION_ADMIN_EMAIL)]

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PGDATABASE', 'zeus'),
        'USER': os.environ.get('PGUSER', 'zeus'),
        'PASS': os.environ.get('PGPASSWORD', ''),
        'HOST': os.environ.get('PGHOST', ''),
        'PORT': os.environ.get('PGPORT', '5432'),
    }
}

OAUTH = {
    'ENABLED': get_from_env('OAUTH_ENABLED', False),
    'VOTER_LOGIN_ENABLED': get_from_env('OAUTH_VOTER_LOGIN_ENABLED', False),
    'TYPE': get_from_env('OAUTH_TYPE', 'discord'),
    'CLIENT_ID': get_from_env('OAUTH_CLIENT_ID', None),
    'CLIENT_SECRET': get_from_env('OAUTH_CLIENT_SECRET', None),
    'DISCORD_SERVER_ID': get_from_env('OAUTH_DISCORD_SERVER_ID', None),
    'DISCORD_ADMIN_ROLE_ID': get_from_env('OAUTH_DISCORD_ADMIN_ROLE_ID', None),
    'AUTHORIZATION_URL': get_from_env('OAUTH_AUTHORIZATION_URL', None),
    'TOKEN_URL': get_from_env('OAUTH_TOKEN_URL', None),
    'USER_INFO_URL': get_from_env('OAUTH_USER_INFO_URL', None),
    'CREATE_ADMIN_IF_DOES_NOT_EXIST': get_from_env('OAUTH_CREATE_ADMIN', True),
    'CREATE_ADMIN_INSTITUTION_ID': get_from_env('OAUTH_ADMIN_INSTITUTION_ID', 1),
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Warsaw'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = get_from_env('LANGUAGE_CODE', 'en')
LANGUAGES = [('en', _('English')), ('el', _('Greek')), ('pl', _('Polish'))]

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/zeus/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
#ADMIN_MEDIA_PREFIX = '/media/'
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(ROOT_PATH, 'sitestatic')

# Make this unique, and don't share it with anybody.
SECRET_KEY = get_from_env('SECRET_KEY', 'replaceme')
# For backwards compatibility
if 'ZEUS_PROD_SECRET_KEY' in os.environ:
    SECRET_KEY = os.environ['ZEUS_PROD_SECRET_KEY']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            ROOT_PATH,
            os.path.join(ROOT_PATH, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.csrf",
                "zeus.context_processors.user",
                "zeus.context_processors.confirm_messages",
                "zeus.context_processors.theme",
                "zeus.context_processors.lang",
                "zeus.context_processors.prefix",
            ],
        },
    },
]


MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'dj_pagination.middleware.PaginationMiddleware',
    'zeus.middleware.AuthenticationMiddleware',
    'zeus.middleware.ExceptionsMiddleware',
]

ROOT_URLCONF = 'urls'

BOOTH_PATH = os.path.join('zeus', 'static', 'booth')

LOCALE_PATHS = (os.path.join(BOOTH_PATH, 'locale'),)

INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'dj_pagination',
    'heliosauth',
    'helios',
    'zeus',
    'server_ui',
    'account_administration',
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

##
## HELIOS
##

HELIOS_CRYPTOSYSTEM_PARAMS = {}
HELIOS_CRYPTOSYSTEM_PARAMS['p'] = 19936216778566278769000253703181821530777724513886984297472278095277636456087690955868900309738872419217596317525891498128424073395840060513894962337598264322558055230566786268714502738012916669517912719860309819086261817093999047426105645828097562635912023767088410684153615689914052935698627462693772783508681806906452733153116119222181911280990397752728529137894709311659730447623090500459340155653968608895572426146788021409657502780399150625362771073012861137005134355305397837208305921803153308069591184864176876279550962831273252563865904505239163777934648725590326075580394712644972925907314817076990800469107
HELIOS_CRYPTOSYSTEM_PARAMS['q'] = 9968108389283139384500126851590910765388862256943492148736139047638818228043845477934450154869436209608798158762945749064212036697920030256947481168799132161279027615283393134357251369006458334758956359930154909543130908546999523713052822914048781317956011883544205342076807844957026467849313731346886391754340903453226366576558059611090955640495198876364264568947354655829865223811545250229670077826984304447786213073394010704828751390199575312681385536506430568502567177652698918604152960901576654034795592432088438139775481415636626281932952252619581888967324362795163037790197356322486462953657408538495400234553
HELIOS_CRYPTOSYSTEM_PARAMS['g'] = 19167066187022047436478413372880824313438678797887170030948364708695623454002582820938932961803261022277829853214287063757589819807116677650566996585535208649540448432196806454948132946013329765141883558367653598679571199251774119976449205171262636938096065535299103638890429717713646407483320109071252653916730386204380996827449178389044942428078669947938163252615751345293014449317883432900504074626873215717661648356281447274508124643639202368368971023489627632546277201661921395442643626191532112873763159722062406562807440086883536046720111922074921528340803081581395273135050422967787911879683841394288935013751

MEDIA_ROOT = MEDIA_ROOT

# a relative path where voter upload files are stored
VOTER_UPLOAD_REL_PATH = "voters/%Y/%m/%d"

LOGIN_URL = '/auth/'
LOGOUT_ON_CONFIRMATION = False


# IMPORTANT: you should not change this setting once you've created
# elections, as your elections' cast_url will then be incorrect.
# SECURE_URL_HOST = "https://localhost"
ZEUS_PROD_HOST = os.environ.get('ZEUS_PROD_HOST', 'localhost')
if get_from_env('ZEUS_PROD_USE_HTTPS', True) == True:
    URL_PREFIX = 'https://'
else:
    URL_PREFIX = 'http://'
URL_HOST = SECURE_URL_HOST = URL_PREFIX + ZEUS_PROD_HOST

ALLOWED_HOSTS = ['localhost', ZEUS_PROD_HOST]
SITE_DOMAIN = ZEUS_PROD_HOST

# election stuff
SITE_TITLE = get_from_env('SITE_TITLE', 'Zeus election server')

# FOOTER links
FOOTER_LINKS = []
FOOTER_LOGO = False

WELCOME_MESSAGE = get_from_env('WELCOME_MESSAGE', "This is the default message")

AUTH_TEMPLATE_BASE = "server_ui/templates/base.html"
HELIOS_TEMPLATE_BASE = "server_ui/templates/base.html"
HELIOS_ADMIN_ONLY = False
HELIOS_VOTERS_UPLOAD = True
HELIOS_VOTERS_EMAIL = True

SHUFFLE_MODULE = 'zeus.zeus_sk'

# are elections private by default?
HELIOS_PRIVATE_DEFAULT = False

# authentication systems enabled
AUTH_ENABLED_AUTH_SYSTEMS = ['password']
AUTH_DEFAULT_AUTH_SYSTEM = None

# email settings
EMAIL_SUBJECT_PREFIX = '[ZEUS] '
DEFAULT_FROM_EMAIL = get_from_env('DEFAULT_FROM_EMAIL', 'zeus.from@localhost')
DEFAULT_FROM_NAME = get_from_env('DEFAULT_FROM_NAME', 'Zeus admin')
SERVER_EMAIL = '%s <%s>' % (DEFAULT_FROM_NAME, DEFAULT_FROM_EMAIL)

HELP_EMAIL_ADDRESS = get_from_env('HELP_EMAIL_ADDRESS', 'zeus.help@localhost')
if os.environ.get('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = get_from_env('EMAIL_HOST', 'localhost')
    EMAIL_PORT = get_from_env('EMAIL_PORT', 587)
    EMAIL_HOST_USER = get_from_env('EMAIL_HOST_USER', None)
    EMAIL_HOST_PASSWORD = get_from_env('EMAIL_HOST_PASSWORD', None)
    EMAIL_USE_TLS = get_from_env('EMAIL_USE_TLS', True)
    EMAIL_USE_SSL = get_from_env('EMAIL_USE_SSL', False)
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# set up logging
#import logging
#logging.basicConfig(
    #level = logging.INFO if DEBUG else logging.INFO,
    #format = '%(asctime)s %(levelname)s %(message)s'
#)

CELERY_BROKER_URL = 'redis://redis'
CELERY_RESULT_BACKEND = 'redis://broker'

BOOTH_STATIC_PATH = ROOT_PATH + '/zeus/static/booth/'

ECOUNTING_LOGIN_URL = "https://x.x.x.x/checkuser.php"
ECOUNTING_POST_URL = "https://x.x.x.x/newelection.php"
ECOUNTING_CHECK_URL = "https://x.x.x.x/newelection.php"
ECOUNTING_SECRET = "xxxxx"

ZEUS_VOTER_EMAIL_RATE = '30/m'

DATA_PATH = os.path.join(ROOT_PATH, 'data')

ZEUS_ELECTION_LOG_DIR = os.path.join(DATA_PATH, 'election_logs')
ZEUS_RESULTS_PATH = os.path.join(DATA_PATH, 'results')
ZEUS_PROOFS_PATH = os.path.join(DATA_PATH, 'proofs')
ZEUS_MIXES_PATH = os.path.join(DATA_PATH, 'mixes')
ZEUS_ALLOW_EARLY_ELECTION_CLOSE = True
ZEUS_CELERY_TEMPDIR = os.path.join('/', 'var', 'run', 'zeus-celery')
ZEUS_HEADER_BG_URL = '/static/zeus/images/logo_bg_nobrand'
ZEUS_TERMS_FILE = os.path.join(ROOT_PATH, 'terms/terms_%(lang)s.html.example')

SERVER_PREFIX = ''

CANDIDATES_CHANGE_TIME_MARGIN = 1

COLLATION_LOCALE = 'el_GR.UTF-8'

MIX_PART_SIZE = 104857600

USE_X_SENDFILE = False

DEMO_MAX_ELECTIONS = 5
DEMO_MAX_VOTERS = 5
DEMO_SUBMIT_INTERVAL_SECONDS = 10
DEMO_EMAILS_PER_IP = 1

MAX_QUESTIONS_LIMIT = 20

PAGINATION_DEFAULT_WINDOW = 3

# apt-get install ttf-dejavu
DEFAULT_REGULAR_FONT = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf"
DEFAULT_BOLD_FONT = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-Bold.ttf"

ZEUS_RESULTS_FONT_REGULAR_PATH = DEFAULT_REGULAR_FONT
ZEUS_RESULTS_FONT_BOLD_PATH = DEFAULT_BOLD_FONT

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Necessary for uploading decryption factors.
DATA_UPLOAD_MAX_MEMORY_SIZE = 30 * 1024 * 1024

TEST_RUNNER = "django.test.runner.DiscoverRunner"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'
        },
        'verbose': {
            'format': 'zeus: %(process)d [%(levelname)s] %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': [],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        # disabled under Docker
        #
        # 'syslog': {
        #    'level': 'INFO',
        #    'class': 'logging.handlers.SysLogHandler',
        #    'address': '/dev/log',
        #    'formatter': 'verbose'
        # },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'include_html': False,
        },
    },
    'loggers': {
        'django': {
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': True,
    },
}


# Session age for users, in seconds.
VOTER_SESSION_AGE = 10 * 60
TRUSTEE_SESSION_AGE = 2 * 60 * 60
USER_SESSION_AGE = 14 * 24 * 60 * 60

SESSION_COOKIE_AGE = USER_SESSION_AGE
