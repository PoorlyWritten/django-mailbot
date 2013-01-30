import logging
logger = logging.getLogger(__name__)
from django.core.mail import EmailMultiAlternatives
from django.template.loader import TemplateDoesNotExist, get_template, Context
from models import TemplatedEmailMessage

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

#def request_feedback_email(to_email, connector_name, link):
#    subject, from_email, to = "I'd like to make better introductions for you", '%s via introduction.es <my@introduction.es>' % connector_name, to_email
#    text_content = "%s wants to know how the introduction went.\n\nDid it lead to something already or is it still building?\n%s\n-%s" % (connector_name, link, connector_name)
#    html_content = "<p>%s want's to know how the introduction went.</p><p>Did it lead to something already or is it still building?</p><p><a href=\"%s\">%s</a></p><p>-%s" % (connector_name, link, link, connector_name)
#    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
#    msg.attach_alternative(html_content, "text/html")
#    logger.debug("trying to send message to %s about %s " % (msg.to, msg.subject))
#    logger.debug(msg.message())
#    try:
#        msg.send()
#    except Exception, error:
#        logger.debug("Couldn't send the mail for %s" % error)
#        logger.debug(msg.subject)
#        logger.debug(msg.recipients())
#        logger.debug(msg.message())

def request_feedback_email(to_email, connector_name, other_email, link):
    template = TemplatedEmailMessage.object.get(name="RequestFeedback")
    context_dict = dict(
                    connector_name = connector_name,
                    other_email = other_email,
                    link = link,
                    )
    template.send(
        from_email = "My Intros <my@intros.to>",
        to_email = to_email,
        context_dict = context_dict
    )
