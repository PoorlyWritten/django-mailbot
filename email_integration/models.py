import logging
logger = logging.getLogger(__name__)
from django.db import models
from django_extensions.db.fields import UUIDField
from django.db import transaction
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import email
import hashlib
import re
import os

class TemplatedEmailMessage(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=512)
    subject = models.CharField(max_length=512)
    text_content = models.TextField()
    html_content = models.TextField(null=True, blank=True)

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
        return m.group('name').lstrip().rstrip()
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


def _extract_emails(msg, header_key):
    addresses = []
    for each in msg.get(header_key,'').replace('\n', '').replace('\t', '').split(','):
        if each:
            print "Working with address: %s " % each
            addr = _tx_create_email_address(each)
            if addr:
                addresses.append(addr)
        return addresses


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
        return self.msg.get(header_name, '').replace('\n','').lstrip().rstrip()

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
        for each in self.isolated_to:
            logger.debug("working with recipient: '%s'" % each)
            _tx_create_email_address(each)
        for each in self.isolated_bcc:
            logger.debug("working with recipient: '%s'" % each)
            _tx_create_email_address(each)
        for each in self.isolated_cc:
            logger.debug("working with recipient: '%s'" % each)
            _tx_create_email_address(each)
        _tx_create_email_address(self.isolated_from_addr)


class EmailAddressManager(models.Manager):
    def get_or_create_email(self, email_address, **kwargs):
        normalized_email = isolate_email(email_address)
        validate_email(normalized_email) #will throw exception on error
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
    date_added = models.DateTimeField(auto_now_add=True)
    address_hash = models.CharField(max_length=128, null=True, blank=True, unique=True)
    verification_hash = models.CharField(max_length=128, null=True, blank=True)
    verification_email_sent = models.DateTimeField(null=True)
    verification_complete = models.BooleanField(default=False)
    objects = EmailAddressManager()

    def __unicode__(self):
        return self.email_address


from django.db.models.signals import post_save

def create_emails(sender, **kwargs):
    instance = kwargs['instance']
    instance.create_emails()

def create_emailprofile(sender, **kwargs):
    user = kwargs['instance']
    user_profile, created = EmailProfile.objects.get_or_create(user=user)
    if created:
        logger.debug("Created profile for %s" % user_profile.user.email)
    email_addr, crated = EmailAddress.objects.get_or_create_email(user.email,
                                                          verification_complete=True,
                                                          user_profile = user_profile)
    if created:
        logger.debug("Created email_address for %s" % user.email)
    logger.debug("user for %s is %s" % (user.email, email_addr.user_profile.user))
    email_addr.save()


post_save.connect(create_emails, sender=RawEmail)
post_save.connect(create_emailprofile, sender=User)
