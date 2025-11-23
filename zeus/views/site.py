
import os
import logging
import uuid
import json
import subprocess

from collections import defaultdict
from time import time
from random import randint

from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _, get_language
from django.contrib import messages
from django.conf import settings
from django.views.i18n import set_language
from django.forms.formsets import formset_factory

from helios.view_utils import render_template
from django.contrib.auth.hashers import make_password
from helios.models import User, Election
from heliosauth.models import UserGroup
from zeus.models import Institution
from zeus.utils import email_is_valid
from zeus.auth import ZeusUser

from zeus.stv_count_reports import stv_count_and_report

logger = logging.getLogger(__name__)


def stv_count(request):

    context = {'menu_active': 'home'}
    session = request.session.get('stvcount', {})
    results_generated = context['results'] = session.get('results', {})
    el_data = None

    do_count = True
    if request.GET.get('form', None):
        do_count = False
        from zeus.forms import STVElectionForm, STVBallotForm
        form = STVElectionForm()

        ballots_form = None
        if request.method == "POST":
            form = STVElectionForm(request.POST, disabled=False)
            if form.is_valid():
                ballots = form.get_ballots()
                el = form.get_data()
                for i, ballot in enumerate(ballots):
                    ballot = ballots[i]
                    choices=[]
                    for j, choice in enumerate(ballot.split(",")):
                        choices.append({'rank': j+1, "candidateTmpId": choice})
                    el['ballots'].append({'votes': choices, "ballotSerialNumber": i})
                el_data = el
                do_count = True

        context['import'] = 1
        context['form'] = form
        context['ballots_form'] = ballots_form

    if request.GET.get('reset', None):
        del request.session['stvcount']
        return HttpResponseRedirect(reverse('stv_count'))

    if request.GET.get('download', None) and results_generated:
        filename = results_generated.get(request.GET.get('download', 'pdf'), '/nofile')
        if not os.path.exists(filename):
            return HttpResponseRedirect(reverse('stv_count') + "?reset=1")

        response = FileResponse(open(filename, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
        response['Content-Length'] = os.path.getsize(filename)
        return response

    if request.method == "POST" and do_count:
        el_data = el_data or json.loads(request.FILES.get('data').read())
        _uuid = str(uuid.uuid4())
        files = stv_count_and_report(_uuid, el_data)
        json_file = os.path.join('/tmp', 'json-stv-results-%s' % _uuid)
        with open(json_file, 'w', encoding="utf-8") as f:
            f.write(json.dumps(el_data, ensure_ascii=False))
        files.append(('json', json_file))
        session['results'] = dict(files)
        request.session['stvcount'] = session
        return HttpResponseRedirect(reverse('stv_count'))

    request.session['stvcount'] = session
    return render_template(request, "zeus/stvcount", context)


def setlang(request):
    lang = request.POST.get('language')
    if lang not in [x[0] for x in settings.LANGUAGES]:
        return HttpResponseRedirect(reverse('home'))
    return set_language(request)


def home(request):
    user = request.zeususer
    bad_login = request.GET.get('bad_login')
    return render_template(request, "zeus/home", {
        'menu_active': 'home',
        'user': user,
        'bad_login': bad_login
    })


def terms(request):
    terms_file = getattr(settings, 'ZEUS_TERMS_FILE', None)
    if terms_file is None:
        return HttpResponseRedirect(reverse('home'))

    with open(terms_file % {'lang': get_language()}, "r") as terms_fd:
        terms_contents = terms_fd.read()

    return render_template(request, "zeus/terms", {
        'content': terms_contents
    })


def faqs_trustee(request):
    user = request.zeususer
    return render_template(request, "zeus/faqs_admin", {
        'menu_active': 'faqs',
        'submenu': 'admin',
        'user': user
    })


def faqs_voter(request):
    user = request.zeususer
    return render_template(request, "zeus/faqs_voter", {
      'menu_active': 'faqs',
      'submenu': 'voter',
      'user': user
    })


def resources(request):
    user = request.zeususer
    return render_template(request, "zeus/resources", {
        'menu_active': 'resources',
        'user': user
    })


def contact(request):
    user = request.zeususer
    return render_template(request, "zeus/contact", {
        'menu_active': 'contact',
        'user': user
    })


def stats(request):
    user = request.zeususer._user
    if not request.zeususer.is_admin:
        return HttpResponseRedirect(reverse('home'))
    uuid = request.GET.get('uuid', None)
    election = None

    elections = Election.objects.filter()
    if not (user and user.superadmin_p):
        elections = Election.objects.filter(canceled_at__isnull=True,
                                            completed_at__isnull=False,
                                            voting_ended_at__isnull=False,
                                            admins__in=[user],
                                            trial=False)

    elections = elections.order_by('-created_at')

    if uuid:
        try:
            election = elections.get(uuid=uuid)
        except Election.DoesNotExist:
            return HttpResponseRedirect(reverse('home'))

    return render_template(request, 'zeus/stats', {
        'menu_active': 'stats',
        'election': election,
        'uuid': uuid,
        'user': user,
        'elections': elections
    })


def error(request, code=None, message=None, type='error'):
    user = getattr(request, 'zeususer', ZeusUser.from_request(request))
    messages_len = len(messages.get_messages(request))
    if not messages_len and not message:
        return HttpResponseRedirect(reverse('home'))

    response = render_template(request, "zeus/error", {
        'code': code,
        'error_message': message,
        'error_type': type,
        'user': user,
    })
    response.status_code = int(code)
    return response


def handler403(request, exception):
    msg = _("You do not have permission to access this page.")
    return error(request, 403, msg)


def handler500(request):
    msg = _("An error has been occured. Please notify the server admin.")
    return error(request, 500, msg)


def handler400(request, exception):
    msg = _("An error has been occured. Please notify the server admin.")
    return error(request, 400, msg)


def handler404(request, exception):
    msg = _("The requested page was not found.")
    return error(request, 404, msg)


def commit(request):
    output = subprocess.check_output(
        ['git', 'log', '-n1'],
        cwd=settings.ROOT_PATH,
        encoding='utf-8',
        errors='ignore'
    )
    return HttpResponse(output, content_type='text/plain; charset=utf-8')
