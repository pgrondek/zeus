
import logging
import six.moves.urllib.request
import six.moves.urllib.error
import six.moves.urllib.parse

from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.shortcuts import redirect

from zeus import auth
from zeus.utils import poll_reverse
from zeus.forms import ChangePasswordForm, VoterLoginForm

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _

from helios.view_utils import render_template
from helios.models import Voter, Poll
from zeus.forms import LoginForm

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
                messages.error(request, 'oauth2 user does not match voter')
                return HttpResponseRedirect(reverse('error',
                                                    kwargs={'code': 400}))
        except six.moves.urllib.error.HTTPError as e:
            poll.logger.exception(e)
            messages.error(request, 'oauth2 error')
            return HttpResponseRedirect(reverse('error',
                                                kwargs={'code': 400}))
    else:
        poll.logger.info("[thirdparty] oauth2 '%s' can_exchange failed",
                         poll.remote_login_display)
        messages.error(request, 'oauth2 exchange failed')
        return HttpResponseRedirect(reverse('error', kwargs={'code': 400}))
