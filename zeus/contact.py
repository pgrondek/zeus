
from email.utils import formataddr
from django.conf import settings
from django.utils import translation
from django.core.mail import EmailMessage, EmailMultiAlternatives
from helios.view_utils import render_template_raw


class ContactError(Exception):
    pass


class ContactBackend():

    Error = ContactError

    def __init__(self, logger, data=None):
        self.logger = logger
        self.data = data

    def can_notify(self, voter):
        raise NotImplementedError

    def render_template(self, tpl, tpl_vars):
        return render_template_raw(None, tpl, tpl_vars)

    @staticmethod
    def should_fallback_to_email(poll, voter, methods):
        if 'email' in voter.contact_methods:
            return True
        return False

    @staticmethod
    def get_backend(method, logger, data=None):
        assert method in ['email']
        if method == 'email':
            return EmailBackend(logger)

    @staticmethod
    def notify_voter(poll, voter, id, methods, subjects, bodies, the_vars,
                     sent_hook=lambda x, y, z: x,
                     attachments=None, sender=None,
                     notify_once=False):

        logger = poll.logger

        if not notify_once and 'email' not in methods and ContactBackend.should_fallback_to_email(poll, voter, methods):
            logger.info("Fallback to email for voter %s", voter.voter_login_id)
            methods = ['email']

        notified = False
        for method in methods:
            if method not in voter.contact_methods:
                continue
            if notify_once and notified:
                continue
            assert method in subjects
            assert method in bodies
            data = None
            backend = ContactBackend.get_backend(method, logger, data)

            lang = poll.election.communication_language
            with translation.override(lang):
                subject_tpl = subjects.get(method)
                body_tpl = bodies.get(method)
                subject = None
                if subject_tpl:
                    subject = backend.render_template(subject_tpl, the_vars)
                body = backend.render_template(body_tpl, the_vars)
                logger.error("Template ", body_tpl)
                if body_tpl == 'vote_body.txt':
                    html_body = backend.render_template('vote_body.html', the_vars)
                else:
                    html_body = None

            backend.notify(voter, id, subject, body, attachments, sent_hook, html_body)
            notified = True

        if not notified:
            logger.error("Voter not notified %r" % (voter.voter_login_id))

    def notify(self, voter, id, subject, body, attachments, sent_hook, html_body=None):
        try:
            result, error = self.do_notify(voter, id, subject, body, attachments, html_body)
        except ContactBackend.Error as e:
            self.logger.exception(e)
            return False
        sent_hook(voter, result, error)

class EmailBackend(ContactBackend):

    def do_notify(self, voter, id, subject, body, attachments, html_body=None):
        self.logger.info("Notifying voter %r for '%r' via email (%r)" % (voter.voter_login_id, id, voter.voter_email))
        subject = subject.replace("\n", "")
        if attachments and len(attachments) > 0:
            name = "%s %s" % (voter.voter_name, voter.voter_surname)
            to = formataddr((name, voter.voter_email))
            if html_body is None:
                message = EmailMessage(subject, body, settings.SERVER_EMAIL, [to])
            else:
                message = EmailMultiAlternatives(subject, body, settings.SERVER_EMAIL, [to])
                message.attach_alternative(html_body, "text/html")
            for attachment in attachments:
                message.attach(*attachment)
            try:
                return message.send(fail_silently=False), None
            except Exception as e:
                return None, e
        else:
            return voter.user.send_message(subject, body), None
