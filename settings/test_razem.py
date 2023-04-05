from .prod import *  # noqa

ADMIN_NAME = 'TEST PKW Razem'
ADMIN_EMAIL = 'razem.pkw@gmail.com'

ADMINS = [
    ('PKW Gmail', 'razem.pkw@gmail.com'),
    ('Grzegorz Kawka-Osik', 'mivalsten@gmail.com'),
]
ELECTION_ADMINS = ADMINS
MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = 'kkw-test@partiarazem.pl'
SERVER_EMAIL = '%s <%s>' % (DEFAULT_FROM_NAME, DEFAULT_FROM_EMAIL)

HELP_EMAIL_ADDRESS = 'kkw@partiarazem.pl'
