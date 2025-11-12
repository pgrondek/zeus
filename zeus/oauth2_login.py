
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


def get_oauth2_module(poll, callback_page):
    return OAUTH2_REGISTRY.get(poll.oauth2_type)(poll, callback_page)


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


class Oauth2Base(object):

    def __init__(self, poll, callback_page):
        self.poll = poll
        self.exchange_url = poll.oauth2_exchange_url
        self.confirmation_url = self.poll.oauth2_confirmation_url
        callback_url = oauth2_callback_url(callback_page)
        self.code_post_data = {
            'response_type': 'code',
            'client_id': poll.oauth2_client_id,
            'redirect_uri': callback_url,
            }

        self.exchange_data = {
            'client_id': poll.oauth2_client_id,
            'client_secret': poll.oauth2_client_secret,
            'redirect_uri': callback_url,
            'grant_type': 'authorization_code',
            }

    def get_code_url(self):
        code_data = self.code_post_data
        encoded_data = six.moves.urllib.parse.urlencode(code_data)
        url = "{}?{}".format(self.poll.oauth2_code_url, encoded_data)
        return url

    def can_exchange(self, request):
        if (request.GET.get('code')):
            self.code = request.GET.get('code')
            # self.session_email = request.session['oauth2_admin_email']
            # self.voter_uuid = request.session.get('oauth2_admin_uuid')
            return True

    def get_exchange_url(self):
        self.exchange_data['code'] = self.code
        encoded_data = six.moves.urllib.parse.urlencode(self.exchange_data)
        return (self.exchange_url, encoded_data)

    def get_username(self):
        raise NotImplementedError

    def get_email(self):
        raise NotImplementedError

    def exchange(self, url):
        raise NotImplementedError

@oauth2_login_module
class Oauth2Other(Oauth2Base):

    type_id = 'other'

    def __init__(self, poll, callback_page):
        super(Oauth2Other, self).__init__(poll, callback_page)
        self.code_post_data['scope'] = 'openid profile email offline_access'

    def exchange(self, url):
        response = six.moves.urllib.request.urlopen(url[0], data = url[1].encode('utf-8'))
        data = json.loads(response.read())
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.id_token = data['id_token']
        self.token_type = data['token_type']
        self.expires_in = data['expires_in']

    def get_username(self):
        request = six.moves.urllib.request.Request(self.confirmation_url)
        request.add_header("Authorization", f"Bearer {self.access_token}")
        response = six.moves.urllib.request.urlopen(request)
        resp = response.read()
        data = json.loads(resp)
        username = data

        if 'nickname' in data:
            username = data['nickname']
        return username

@oauth2_login_module
class Oauth2Discord(Oauth2Base):

    type_id = 'discord'

    def __init__(self, poll, callback_page):
        super(Oauth2Discord, self).__init__(poll, callback_page)
        self.code_post_data['scope'] = 'identify email'

    def exchange(self, url):
        request = six.moves.urllib.request.Request(url[0], data = url[1].encode('utf-8'), method="POST")
        request.add_header("Content-Type", "application/x-www-form-urlencoded")
        request.add_header("User-Agent", "Zeus-ng app")
        response = six.moves.urllib.request.urlopen(request)
        data = json.loads(response.read())
        self.access_token = data['access_token']

    def get_exchange_url(self):
        self.exchange_data['code'] = self.code
        self.exchange_data['grant_type'] = 'authorization_code'
        self.exchange_data['client_id'] = self.poll.oauth2_client_id
        self.exchange_data['client_secret'] = self.poll.oauth2_client_secret

        encoded_data = six.moves.urllib.parse.urlencode(self.exchange_data)
        return (self.exchange_url, encoded_data)

    def get_username(self):
        request = six.moves.urllib.request.Request(self.confirmation_url)
        request.add_header("Authorization", f"Bearer {self.access_token}")
        request.add_header("User-Agent", "Zeus-ng app")
        response = six.moves.urllib.request.urlopen(request)
        resp = response.read()
        data = json.loads(resp)
        username = data

        if 'username' in data:
            username = data['username']
        return username

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
