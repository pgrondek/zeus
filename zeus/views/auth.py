
import logging

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.shortcuts import redirect
from kombu.abstract import Object

from heliosauth.models import User
from zeus import auth
from zeus.utils import poll_reverse
from zeus.forms import ChangePasswordForm, VoterLoginForm

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from helios.view_utils import render_template
from zeus import auth
from zeus.forms import ChangePasswordForm, VoterLoginForm
from zeus.forms import LoginForm
from zeus.utils import poll_reverse

logger = logging.getLogger(__name__)


@auth.unauthenticated_user_required
@require_http_methods(["POST", "GET"])
def voter_login(request):
    form = VoterLoginForm()
    if request.method == 'POST':
        form = VoterLoginForm(request.POST)
        if form.is_valid():
            poll = form._voter.poll
            user = auth.ZeusUser(form._voter)
            user.authenticate(request)
            poll.logger.info("Poll voter '%s' logged in (global login view)",
                             form._voter.voter_login_id)
            return HttpResponseRedirect(poll_reverse(poll, 'index'))

    cxt = {'form': form}
    return render_template(request, 'voter_login', cxt)


@auth.unauthenticated_user_required
@require_http_methods(["POST", "GET"])
def password_login_view(request):
    error = None
    if request.method == "GET":
        form = LoginForm()
    else:
        form = LoginForm(request.POST)

    request.session['auth_system_name'] = 'password'

    if request.method == "POST":
        if form.is_valid():
            request.session[auth.USER_SESSION_KEY] = form._user_cache.pk
            logger.info("User %s logged in", form._user_cache.user_id)
            return HttpResponseRedirect(reverse('admin_home'))

    return render_template(request,
                           'login',
                           {'form': form, 'error': error})

@auth.unauthenticated_user_required
def oauth2_admin_login(request):
    fake_poll= Object()
    from zeus import oauth2_login

    fake_poll.oauth2_type = 'other'
    fake_poll.oauth2_exchange_url = 'https://auth.grondek.pl/application/o/token/'# token url
    fake_poll.oauth2_code_url = 'https://auth.grondek.pl/application/o/authorize/'# Authorization url
    fake_poll.oauth2_confirmation_url ='https://auth.grondek.pl/application/o/userinfo/'# User info
    fake_poll.oauth2_client_id = ''
    fake_poll.oauth2_client_secret = ''

    oauth2 = oauth2_login.get_oauth2_module(fake_poll)
    if oauth2.can_exchange(request):
        exchange_url = oauth2.get_exchange_url()
        oauth2.exchange(exchange_url)
        try:
            username = oauth2.get_username()
            try:
                user = User.objects.get(user_id=username)
                request.session[auth.USER_SESSION_KEY] = user.pk
                return HttpResponseRedirect(reverse('error', kwargs={'code': 400}))
            except User.DoesNotExist:
                messages.error(request, 'oauth2 user does not match admin')
                return HttpResponseRedirect(reverse('error', kwargs={'code': 400}))
        except six.moves.urllib.error.HTTPError as e:
            messages.error(request, e.reason)
            return HttpResponseRedirect(reverse('error',
                                                kwargs={'code': 400}))
    else:
        url = oauth2.get_code_url()
        logger.info("[thirdparty] code handshake from %s", url)
        context = {'url': url}
        tpl = 'admin_redirect'
        return render_template(request, tpl, context)

def logout(request):
    return_url = request.GET.get('next', reverse('home'))
    if not request.zeususer.is_authenticated():
        return HttpResponseRedirect(return_url)

    logger.info("User %s logged out", request.zeususer.user_id)
    request.zeususer.logout(request)
    return HttpResponseRedirect(return_url)


@auth.user_required
def change_password(request):
    user = request.zeususer

    # only admin users can change password
    if not user.is_admin:
        raise PermissionDenied('32')

    password_changed = request.GET.get('password_changed', None)
    form = ChangePasswordForm(user)
    if request.method == "POST":
        form = ChangePasswordForm(user._user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse('change_password') + '?password_changed=1')
    return render_template(request, 'change_password',
                           {'form': form,
                            'password_changed': password_changed})
