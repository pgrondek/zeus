
import logging

import six.moves.urllib.error
import six.moves.urllib.parse
import six.moves.urllib.request
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from helios.models import Poll, Voter
from helios.view_utils import render_template
from heliosauth.models import User, UserGroup
from zeus import auth
from zeus.forms import ChangePasswordForm, VoterLoginForm
from zeus.forms import LoginForm
from zeus.models import Institution
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
    from zeus import oauth2_login

    logger.info("Oauth login is: %s", settings.OAUTH['ENABLED'])
    if not settings.OAUTH['ENABLED']:
        messages.error(request, _('Discord admin login not enabled'))
        return HttpResponseRedirect(reverse('login'))

    oauth_config = oauth2_login.get_oauth2_config()

    oauth2 = oauth2_login.get_oauth2_module(oauth_config, 'oauth2_admin_login')
    if oauth2.can_exchange(request):
        exchange_url = oauth2.get_exchange_url()
        oauth2.exchange(exchange_url)
        try:
            email, discord_id, global_name = oauth2.get_user_info()
            user_id = f'discord_{discord_id}'
            if not oauth2.validate_access('admin'):
                messages.error(request, _('You\'re not in required discord server or you don\'t have a required role'))
                return HttpResponseRedirect(reverse('error',
                                                    kwargs={'code': 400}))

            try:
                user = User.objects.get(user_id=user_id)
                request.session[auth.USER_SESSION_KEY] = user.pk
                return HttpResponseRedirect(reverse('admin_home'))
            except User.DoesNotExist:
                if not settings.OAUTH['CREATE_ADMIN_IF_DOES_NOT_EXIST']:
                    messages.error(request, _('Could not find admin account'))
                    return HttpResponseRedirect(reverse('home', kwargs={'code': 400}))

                new_user = User()
                new_user.user_type = "password" # lol
                new_user.admin_p = True
                new_user.info = {'name': global_name, 'authorization': 'discord', 'discord_id': discord_id}
                new_user.email = email
                new_user.name = global_name
                new_user.user_id = user_id
                new_user.superadmin_p = False
                new_user.management_p = False
                new_user.institution = Institution.objects.get(pk=int(settings.OAUTH['CREATE_ADMIN_INSTITUTION_ID']))
                new_user.ecounting_account = False
                new_user.save()
                new_user.user_groups.set([UserGroup.objects.get(name="default")])
                request.session[auth.USER_SESSION_KEY] = new_user.pk
                return HttpResponseRedirect(reverse('admin_home'))

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
    if not user._user.local_account:
        messages.error(request, _('You login trough external authentication, you cannot set password'))
        return HttpResponseRedirect(reverse('error',
                                            kwargs={'code': 403}))

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


@auth.unauthenticated_user_required
def oauth2_login(request):
    poll_uuid = request.GET.get('state')
    try:
        poll = Poll.objects.get(uuid=poll_uuid)
    except Poll.DoesNotExist:
        return HttpResponseBadRequest(400)
    oauth2 = poll.get_oauth2_module
    if oauth2.can_exchange(request):
        oauth2.exchange(oauth2.get_exchange_url())
        try:
            confirmed, data = oauth2.confirm_email()
            if confirmed:
                voter = Voter.objects.get(poll__uuid=poll_uuid,
                                          uuid=oauth2.voter_uuid)
                user = auth.ZeusUser(voter)
                user.authenticate(request)
                poll.logger.info("Poll voter '%s' logged in",
                                 voter.voter_login_id)
                del request.session['oauth2_voter_uuid']
                del request.session['oauth2_voter_email']
                return HttpResponseRedirect(poll_reverse(poll, 'index'))
            else:
                poll.logger.info("[thirdparty] %s cannot resolve email from %r",
                                 poll.remote_login_display, data)
                messages.error(request, _('Cannot confirm voter email'))
                return HttpResponseRedirect(reverse('error',
                                                    kwargs={'code': 400}))
        except six.moves.urllib.error.HTTPError as e:
            poll.logger.exception(e)
            messages.error(request, _('Discord error'))
            return HttpResponseRedirect(reverse('error',
                                                kwargs={'code': 400}))
    else:
        poll.logger.info("[thirdparty] oauth2 '%s' can_exchange failed",
                         poll.remote_login_display)
        messages.error(request, _('Discord error'))
        return HttpResponseRedirect(reverse('error', kwargs={'code': 400}))

@auth.unauthenticated_user_required
def voter_oauth_login(request):
    if not settings.OAUTH['ENABLED'] or not settings.OAUTH['VOTER_LOGIN_ENABLED']:
        logger.error("Discord voter login not enabled")
        messages.error(request, _('Discord voter login not enabled'))
        return HttpResponseRedirect(reverse('home'))

    if request.session.get('oauth2_voter_access_token'):
        return HttpResponseRedirect(reverse('voter_oauth_polls'))

    from zeus import oauth2_login

    oauth_config = oauth2_login.get_oauth2_config()

    oauth2 = oauth2_login.get_oauth2_module(oauth_config, 'voter_oauth_login')
    if oauth2.can_exchange(request):
        exchange_url = oauth2.get_exchange_url()
        oauth2.exchange(exchange_url)
        if not oauth2.validate_access('voter'):
            messages.error(request, _('You\'re not in required discord server'))
            return HttpResponseRedirect(reverse('error',
                                                kwargs={'code': 400}))
        try:
            request.session['oauth2_voter_access_token'] = oauth2.access_token

            return HttpResponseRedirect(reverse('voter_oauth_polls'))

        except six.moves.urllib.error.HTTPError as e:
            messages.error(request, e.reason)
            return HttpResponseRedirect(reverse('error',
                                                kwargs={'code': 400}))
    else:
        url = oauth2.get_code_url()
        logger.info("[thirdparty] code handshake from %s", url)
        context = {'url': url}
        tpl = 'voter_redirect'
        return render_template(request, tpl, context)

def voter_oauth_logout(request):
    del request.session['oauth2_voter_access_token']
    return HttpResponseRedirect(reverse("home"))

def voter_oauth_polls(request):
    if not request.session.get('oauth2_voter_access_token'):
        messages.error(request, _('Missing access token'))
        return HttpResponseRedirect(reverse('voter_oauth_login'))

    from zeus import oauth2_login

    oauth_config = oauth2_login.get_oauth2_config()

    oauth2 = oauth2_login.get_oauth2_module(oauth_config, 'voter_oauth_login')
    oauth2.access_token = request.session.get('oauth2_voter_access_token')

    voter = None
    voter_email = oauth2.get_email()
    polls = Poll.objects.filter(voters__voter_email=voter_email)

    allowed_polls = []
    for poll in polls:
        allowed_polls.append(poll)

    polls_data = []
    for poll in allowed_polls:
        data = [poll]
        voter = poll.voters.get(voter_email=voter_email)
        voter_link = voter.get_quick_login_url()
        data.append(voter_link)
        polls_data.append(data)

    context = {'issuer': 'Zeus', 'voter_data': voter, 'polls_data': polls_data}
    tpl = 'oauth_polls_list'
    return render_template(request, tpl, context)
