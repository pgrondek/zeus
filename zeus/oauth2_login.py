
import json
import six.moves.urllib.request
import six.moves.urllib.parse
import six.moves.urllib.error

from django.conf import settings
from django.urls import reverse

OAUTH2_REGISTRY = {}


def oauth2_login_module(cls):
    OAUTH2_REGISTRY[cls.type_id] = cls
    return cls


def get_oauth2_module(config, callback_page):
    return OAUTH2_REGISTRY.get(config.oauth2_type)(config, callback_page)

def get_oauth2_config():
    oauth_type = settings.OAUTH['TYPE']
    discord = None
    if oauth_type == 'discord':
        discord = Oauth2ConfigDiscord(
            server_id=settings.OAUTH['DISCORD_SERVER_ID'],
            admin_role_id=settings.OAUTH['DISCORD_ADMIN_ROLE_ID'],
        )
    config = Oauth2Config(
        oauth2_type=oauth_type,
        token_url=settings.OAUTH['TOKEN_URL'],
        authorization_url=settings.OAUTH['AUTHORIZATION_URL'],
        user_info_url=settings.OAUTH['USER_INFO_URL'],
        client_id=settings.OAUTH['CLIENT_ID'],
        client_secret=settings.OAUTH['CLIENT_SECRET'],
        discord=discord
    )
    return config


def oauth2_callback_url(callback_page):
    base = settings.SECURE_URL_HOST
    prefix = settings.SERVER_PREFIX
    path = reverse(callback_page)
    if prefix:
        path = prefix + path
    if path.startswith("/"):
        path = path[1:]
    if base.endswith("/"):
        base = base[:-1]

    return "/".join([base, path])

class Oauth2Config:

    def __init__(self, oauth2_type, token_url, authorization_url, user_info_url, client_id, client_secret, discord):
        self.oauth2_type = oauth2_type
        self.token_url = token_url
        self.authorization_url = authorization_url
        self.user_info_url = user_info_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.discord = discord

class Oauth2ConfigDiscord:
    def __init__(self, server_id, admin_role_id):
        self.server_id = server_id
        self.admin_role_id = admin_role_id

class Oauth2Base(object):

    def __init__(self, config:Oauth2Config, callback_page):
        self.config = config
        self.exchange_url = config.token_url
        self.confirmation_url = self.config.user_info_url
        self.authorization_url = config.authorization_url
        callback_url = oauth2_callback_url(callback_page)
        self.code_post_data = {
            'response_type': 'code',
            'client_id': config.client_id,
            'redirect_uri': callback_url,
            }

        self.exchange_data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'redirect_uri': callback_url,
            'grant_type': 'authorization_code',
            }

    def get_code_url(self):
        code_data = self.code_post_data
        encoded_data = six.moves.urllib.parse.urlencode(code_data)
        url = "{}?{}".format(self.authorization_url, encoded_data)
        return url

    def can_exchange(self, request):
        if (request.GET.get('code')):
            self.code = request.GET.get('code')
            return True

    def validate_access(self, role):
        return True

    def get_exchange_url(self):
        self.exchange_data['code'] = self.code
        encoded_data = six.moves.urllib.parse.urlencode(self.exchange_data)
        return (self.exchange_url, encoded_data)

    def get_email(self):
        raise NotImplementedError

    def exchange(self, url):
        raise NotImplementedError

@oauth2_login_module
class Oauth2Other(Oauth2Base):

    type_id = 'other'

    def __init__(self, config, callback_page):
        super(Oauth2Other, self).__init__(config, callback_page)
        self.code_post_data['scope'] = 'openid profile email offline_access'

    def exchange(self, url):
        response = six.moves.urllib.request.urlopen(url[0], data = url[1].encode('utf-8'))
        data = json.loads(response.read())
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.id_token = data['id_token']
        self.token_type = data['token_type']
        self.expires_in = data['expires_in']

    def get_email(self):
        request = six.moves.urllib.request.Request(self.confirmation_url)
        request.add_header("Authorization", f"Bearer {self.access_token}")
        response = six.moves.urllib.request.urlopen(request)
        resp = response.read()
        data = json.loads(resp)
        email = data

        if 'email' in data:
            email = data['email']
        return email

@oauth2_login_module
class Oauth2Discord(Oauth2Base):

    type_id = 'discord'

    def __init__(self, config, callback_page):
        super(Oauth2Discord, self).__init__(config, callback_page)
        self.code_post_data['scope'] = 'identify email guilds guilds.members.read'
        self.exchange_url = 'https://discord.com/api/oauth2/token'
        self.confirmation_url = 'https://discord.com/api/users/@me'
        self.authorization_url = 'https://discord.com/oauth2/authorize'
        self.discord_server_info_url = 'https://discord.com/api/users/@me/guilds'
        self.server_id = config.discord.server_id
        self.admin_role_id = config.discord.admin_role_id

    def exchange(self, url):
        request = six.moves.urllib.request.Request(url[0], data = url[1].encode('utf-8'), method="POST")
        request.add_header("Content-Type", "application/x-www-form-urlencoded")
        request.add_header("User-Agent", "Zeus-ng app")
        response = six.moves.urllib.request.urlopen(request)
        data = json.loads(response.read())
        self.access_token = data['access_token']

    def validate_access(self, role):
        request = six.moves.urllib.request.Request(self.discord_server_info_url)
        request.add_header("Authorization", f"Bearer {self.access_token}")
        request.add_header("User-Agent", "Zeus-ng app")
        response = six.moves.urllib.request.urlopen(request)
        resp = response.read()
        data = json.loads(resp)

        in_required_guild = False
        for server in data:
            if server['id'] == self.server_id:
                in_required_guild = True
        if role == 'voter':
            return in_required_guild
        elif role == 'admin':
            request = six.moves.urllib.request.Request(f'{self.discord_server_info_url}/{self.server_id}/member')
            request.add_header("Authorization", f"Bearer {self.access_token}")
            request.add_header("User-Agent", "Zeus-ng app")
            response = six.moves.urllib.request.urlopen(request)
            resp = response.read()
            data = json.loads(resp)
            is_admin = False

            for role in data['roles']:
                if role == self.admin_role_id:
                    is_admin = True
                    break
            return is_admin
        else:
            return False

    def get_exchange_url(self):
        self.exchange_data['code'] = self.code
        self.exchange_data['grant_type'] = 'authorization_code'
        self.exchange_data['client_id'] = self.config.client_id
        self.exchange_data['client_secret'] = self.config.client_secret

        encoded_data = six.moves.urllib.parse.urlencode(self.exchange_data)
        return self.exchange_url, encoded_data

    def get_email(self):
        request = six.moves.urllib.request.Request(self.confirmation_url)
        request.add_header("Authorization", f"Bearer {self.access_token}")
        request.add_header("User-Agent", "Zeus-ng app")
        response = six.moves.urllib.request.urlopen(request)
        resp = response.read()
        data = json.loads(resp)
        email = 'nobody@localhost'
        verified = False

        if 'email' in data:
            email = data['email']
            verified = data['verified']

        if verified:
            return email
        else:
            return None
