import logging
logger = logging.getLogger(__name__)
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.db import models
from django.db import transaction
from django.template import Template, Context
from django_extensions.db.fields import UUIDField
import email
from email.Header import decode_header
import hashlib
import os
import re

class TemplatedEmailMessage(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=512)
    subject = models.CharField(max_length=512)
    text_content = models.TextField()
    html_content = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def send(self, from_email=settings.DEFAULT_FROM_EMAIL, to_email=None, context_dict=None):
        msg = EmailMultiAlternatives(
            self.subject,
            Template(self.text_content).render(Context(context_dict)),
            from_email,
            [to_email]
        )
        if self.html_content != "":
            tmpl = Template(self.html_content)
            msg.attach_alternative(
                tmpl.render(Context(context_dict)),
                "text/html"
            )
        logger.debug("Sending to %s from %s" %( to_email, from_email))
        msg.send()


def extract_plain_text_body(msg):
    body = None
    for subpart in email.iterators.typed_subpart_iterator(msg, "text", "plain"):
        if body:
            body = "%s\n%s" % (body, subpart._payload)
        else:
            body = subpart._payload
    return body

def isolate_email(address):
    """Apply several regular expressions to detect
    common email addresses and
    return the isolated address
    """
    matches = [
        "(?P<name>[^<].*)<(?P<email>.*)>",
        "<(?P<email>.*)>",
        "(?P<email>.*)"
    ]
    for regex in matches:
        #print "checking %s with %s" % (address, regex)
        m = re.match(r"%s" % regex, address)
        if m:
            return m.group('email').lstrip().rstrip()
    return None

def isolate_name(address):
    m = re.match("(?P<name>[^<].*)<(?P<email>.*)>", address)
    if m:
        return m.group('name').lstrip().rstrip().lstrip('"').rstrip('"')
    return None


@transaction.commit_manually
def _tx_create_email_address(addr):
    try:
        address, created = EmailAddress.objects.get_or_create_email(addr)
        address.save()
        transaction.commit()
    except ValidationError, error:
        print "We've got an address validation problem here for %s : %s" % (addr,error)
        transaction.rollback()
        address = None
    return address


class EmailProfile(models.Model):
    """A class to manage the relationship between e-mail addresses and people"""
    id = UUIDField(primary_key=True, auto=True, version=4)
    user = models.ForeignKey(User)
    date_added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user.__unicode__()


class RawEmail(models.Model):
    """A class to hold raw email"""
    id = UUIDField(primary_key=True, auto=True, version=4)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_parsed = models.DateTimeField(null=True, blank=True)
    parsed = models.BooleanField(default=False)
    parsed_emails = models.BooleanField(default=False)
    msg = None

    def __unicode__(self):
        return u'raw email received at %s' % self.date_added

    def _get_header(self, header_name):
        if not self.msg:
            self.msg = email.message_from_string(self.content)
        header_content = decode_header(self.msg.get(header_name, ''))
        return_content = u''
        for line in header_content:
            str, enc = line
            if enc:
                content = str.decode(enc)
            else:
                content = str.encode('utf-8')
            return_content = u'%s%s' % (return_content, content)
        return return_content.lstrip().rstrip()

    @property
    def to(self):
        return self._get_header('To')
    @property
    def from_addr(self):
        return self._get_header('From')
    @property
    def cc(self):
        return self._get_header('Cc')
    @property
    def bcc(self):
        return self._get_header('Bcc')
    @property
    def delivered_to(self):
        return self._get_header('Delivered-To')
    @property
    def message_id(self):
        return self._get_header('Message-ID')
    @property
    def subject(self):
        return self._get_header('Subject')
    @property
    def payload(self):
        if not self.msg:
            self.msg = email.message_from_string(self.content)
        return extract_plain_text_body(self.msg)
    @property
    def isolated_from_addr(self):
        return isolate_email(self.from_addr)
    @property
    def isolated_to(self):
        return [isolate_email(x).lstrip().rstrip() for x in self.to.split(',') if x != '']
    @property
    def isolated_cc(self):
        return [isolate_email(x) for x in self.cc.split(',')]
    @property
    def isolated_bcc(self):
        return [isolate_email(x) for x in self.bcc.split(',')]
    @property
    def isolated_delivered_to(self):
        return isolate_email(self.delivered_to)
    @property
    def sent_by_name(self):
        return isolate_name(self.from_addr)

    def create_emails(self):
        for each in self._get_header("To").split(','):
            if each != '':
                logger.debug("working with recipient: '%s'" % each)
                _tx_create_email_address(each)
        for each in self._get_header("Bcc").split(','):
            if each != '':
                logger.debug("working with recipient: '%s'" % each)
                _tx_create_email_address(each)
        for each in self._get_header("Cc").split(','):
            if each != '':
                logger.debug("working with recipient: '%s'" % each)
                _tx_create_email_address(each)
        _tx_create_email_address(self.isolated_from_addr)

class EmailAddressManager(models.Manager):
    def get_or_create_email(self, email_address, **kwargs):
        normalized_email = isolate_email(email_address)
        validate_email(normalized_email) #will throw exception on error
        full_name = isolate_name(email_address)
        if full_name:
            kwargs['full_name'] = full_name
        try:
            addr = self.get(email_address=normalized_email)
            logger.debug("Existing email address found for %s" % email_address)
            for key,value in kwargs.iteritems():
                setattr(addr,key, value)
            created = None
        except EmailAddress.DoesNotExist:
            logger.debug("Creating new email address for %s" % email_address)
            addr = self.create_email(normalized_email, **kwargs)
            created = True
        return addr, created

    def create_email(self, email_address, **kwargs):
        normalized_email = isolate_email(email_address)
        validate_email(normalized_email) #will throw exception on error
        attrs = dict(
            email_address=normalized_email,
            address_hash=hashlib.sha1(normalized_email).hexdigest(),
            verification_hash=os.urandom(32).encode('hex'),
            **kwargs
        )
        logger.debug("Creating email with attrs: %s" % attrs)
        return EmailAddress(**attrs)


class EmailAddress(models.Model):
    id = UUIDField(primary_key=True, auto=True, version=4)
    user_profile = models.ForeignKey(EmailProfile, null=True, blank=True)
    email_address = models.EmailField(unique=True)
    full_name = models.CharField(max_length=128, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    address_hash = models.CharField(max_length=128, null=True, blank=True, unique=True)
    verification_hash = models.CharField(max_length=128, null=True, blank=True)
    verification_email_sent = models.DateTimeField(null=True)
    verification_complete = models.BooleanField(default=False)
    objects = EmailAddressManager()

    def __unicode__(self):
        return self.email_address


from django.db.models.signals import post_save, pre_save

def create_emails(sender, **kwargs):
    instance = kwargs['instance']
    instance.create_emails()

def reconcile_names(sender, **kwargs):
    instance = kwargs['instance']
    try:
        first_name, last_name = instance.full_name.split(" ")
        try:
            user = User.objects.get(email=instance.email_address)
            if user.first_name == "" and user.last_name == "":
                user.first_name = first_name
                user.last_name = last_name
                user.save()
        except User.DoesNotExist:
            pass

    except:
        pass


def create_emailprofile(sender, **kwargs):
    user = kwargs['instance']
    user_profile, created = EmailProfile.objects.get_or_create(user=user)
    if created:
        logger.debug("Created profile for %s" % user_profile.user.email)
    email_addr, created = EmailAddress.objects.get_or_create_email(user.email,
                                                          verification_complete=True,
                                                          user_profile = user_profile)
    if created:
        logger.debug("Created email_address for %s" % user.email)
    logger.debug("user for %s is %s" % (user.email, email_addr.user_profile.user))
    try:
        email_addr.save()
    except:
        pass

def send_welcome_email(sender, *args, **kwargs):
    user = kwargs['instance']
    if user.pk == None:
        template = TemplatedEmailMessage.objects.get(name="ConnectorWelcome")
        context_dict = dict(
                connector = user.get_full_name()
                )
        template.send(
        from_email = "Robyn Scott <members@intros.to>",
        to_email = user.email,
        context_dict = context_dict
        )
    else:
        logger.debug("PK for existing user is = %s" %  user.pk)

post_save.connect(create_emails, sender=RawEmail)
post_save.connect(reconcile_names, sender=EmailAddress)
post_save.connect(create_emailprofile, sender=User)
pre_save.connect(send_welcome_email, sender=User)
