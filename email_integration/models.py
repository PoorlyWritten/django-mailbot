import logging
logger = logging.getLogger(__name__)
from django.db import models
from django_extensions.db.fields import UUIDField
from django.db import transaction
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import datetime
import email
import hashlib
import re
import os


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


@transaction.commit_manually
def _tx_create_email_address(addr):
    try:
        address, created = EmailAddress.objects.get_or_create_email(addr)
        address.save()
        transaction.commit()
    except ValidationError:
        print "We've got an address validation problem here: %s" % addr
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
    id = UUIDField(primary_key=True, version=4)
    user = models.ForeignKey(User)
    date_added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user.__unicode__()


class RawEmail(models.Model):
    """A class to hold raw email"""
    id = UUIDField(primary_key=True, version=4)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_parsed = models.DateTimeField(null=True, blank=True)
    parsed = models.BooleanField(default=False)
    parsed_emails = models.BooleanField(default=False)

    def __unicode__(self):
        return u'raw email received at %s' % self.date_added


class EmailAddressManager(models.Manager):
    def get_or_create_email(self, email_address):
        normalized_email = isolate_email(email_address)
        validate_email(normalized_email) #will throw exception on error
        try:
            addr = self.get(email_address=normalized_email)
            print addr.pk
            created = False
        except EmailAddress.DoesNotExist:
            addr = self.create_email(normalized_email)
            created = True
        return addr, created

    def create_email(self, email_address):
        normalized_email = isolate_email(email_address)
        validate_email(normalized_email) #will throw exception on error
        return EmailAddress(
            email_address=normalized_email,
            address_hash=hashlib.sha1(normalized_email).hexdigest(),
            verification_hash=os.urandom(32).encode('hex'))


class EmailAddress(models.Model):
    id = UUIDField(primary_key=True, version=4)
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


class ParsedEmailManager(models.Manager):

    def create_parsed_email(self, raw_message=None):
        msg = email.message_from_string(raw_message.content)

        if msg.is_multipart():
            content = u''
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    content = u'%s\n%s' % (content, unicode(part))
        else:
            content = msg.get_payload()

        parsed = self.create(
            raw_message=raw_message,
            message_id=msg.get('Message-ID',''),
            subject=msg.get('Subject','').lstrip().rstrip(),
            content = content,
        )

        raw_message.parsed = True
        raw_message.parsed_emails = True
        raw_message.date_parsed = datetime.datetime.now()
        raw_message.save()


class ParsedEmail(models.Model):
    id = UUIDField(primary_key=True, version=4)
    raw_message = models.ForeignKey(RawEmail, editable=False)
    message_id = models.CharField(max_length=128, unique=True, blank=False, null=False)
    from_email = models.ManyToManyField(EmailAddress, related_name='from_addresses', null=True, blank=True, editable=False)
    to_email = models.ManyToManyField(EmailAddress, related_name='to_addresses', null=True, blank=True, editable=False)
    cc_email = models.ManyToManyField(EmailAddress, related_name='cc_addresses', null=True, blank=True, editable=False)
    bcc_email = models.ManyToManyField(EmailAddress, related_name='bcc_addresses', null=True, blank=True, editable=False)
    subject = models.CharField(max_length=256, null=True, blank=True)
    content = models.TextField(null=True,blank=True)
    objects = ParsedEmailManager()

    def __unicode__(self):
        return self.subject or ''

    @property
    def delivered_to(self):
        msg = email.message_from_string(self.raw_message.content)
        return msg.get('Delivered-To','').replace('\n', '').replace('\t', '')


    @transaction.commit_manually
    def _tx_add_email_address(self, field_name, addr):
        field = getattr(self, field_name, None)
        if field:
            print "Adding to %s: %s [%s]" % (field_name, addr, addr.pk)
            try:
                field.add(self, addr)
                transaction.commit()
            except:
                transaction.rollback()
        transaction.rollback()




    def _parse_email_addresses(self):
        msg = email.message_from_string(self.raw_message.content)
        from_addresses = _extract_emails(msg, 'From')
        to_addresses = _extract_emails(msg, 'To')
        cc_addresses = _extract_emails(msg, 'Cc')
        bcc_addresses = _extract_emails(msg, 'Bcc')
        for each in to_addresses:
            self._tx_add_email_address('to_email', each)
        for each in from_addresses:
            self._tx_add_email_address('from_email', each)
        for each in cc_addresses:
            self._tx_add_email_address('cc_email', each)
        for each in bcc_addresses:
            self._tx_add_email_address('bcc_email', each)


from django.db.models.signals import post_save
from tasks import parse_one_mail, parse_email_from_mail
def parse_mail(sender,**kwargs):
    #{'raw': False, 'instance': <RawEmail: raw email received at 2013-01-15 15:37:39+00:00>, 'signal': <django.dispatch.dispatcher.Signal object at 0x34dd350>, 'using': 'default', 'created': False}
    instance = kwargs['instance']
    logger.debug("In parse_mail where instance.pk = %s" % instance.pk)
    if not instance.parsed:
        parse_one_mail(instance.pk)

def test_signal_handler(sender, **kwargs):
    logger.debug('test_signal_handler - sender = %s' % sender)
    logger.debug('test_signal_handler - instance = %s' % kwargs['instance'])

def extract_emails(sender, *args, **kwargs):
    instance = kwargs['instance']
    if not instance.raw_message.parsed_emails:
        parse_email_from_mail(instance.id)


post_save.connect(test_signal_handler)
post_save.connect(parse_mail, sender=RawEmail)
post_save.connect(extract_emails, sender=ParsedEmail)
