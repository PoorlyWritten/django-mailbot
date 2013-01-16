import logging
logger = logging.getLogger(__name__)
from django.core.mail import EmailMultiAlternatives
from django.template.loader import TemplateDoesNotExist, get_template, Context, render_to_string

def _render_template(template_name, **context):
    try:
        t = get_template(template_name)
        return t.render(Context(context)).strip()
    except TemplateDoesNotExist:
        logger.warning("Couldn't find template % to render for email" % template_name)
        return ''

def send_html_mail(template_name, subject=None, from_email=None, to=None, cc=None, bcc=None, context={} ):
    subject, from_email, to = 'hello', 'from@example.com', 'to@example.com'
    text_content = 'This is an important message.'
    html_content = '<p>This is an <strong>important</strong> message.</p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def send_verification_email(to_email,anon_hash,template='user_emails/verification'):
    subject, from_email, to = 'Please confirm your email address', 'my@introduction.es', to_email
    text_content = 'Please go to http://introduction.es/verify/%s to confirm this email address.\n-alex' % anon_hash
    html_content = 'Please go to <a href="http://introduction.es/verify/%s">introduction.es/verify</a> to confirm this email address.\n-alex' % anon_hash
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
