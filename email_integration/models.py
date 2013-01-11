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

class EmailProfile(models.Model):
    """A class to manage the relationship between e-mail addresses and people"""
    id = UUIDField(primary_key=True, version=4)
    user = models.ForeignKey(User)
    date_added = models.DateTimeField(auto_now_add=True)

class RawEmail(models.Model):
    """A class to hold raw email"""
    id = UUIDField(primary_key=True, version=4)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_parsed = models.DateTimeField(null=True, blank=True)
    parsed = models.BooleanField(default=False)


class EmailAddressManager(models.Manager):
    def get_or_create(self, email_address):
        normalized_email = isolate_email(email_address)
        validate_email(normalized_email) #will throw exception on error
        try:
            return self.get(address_hash=hashlib.sha1(normalized_email))
        except:
            #notfound error
            self.create_email_address(email_address)

    def create_email_address(self, email_address):
        normalized_email = isolate_email(email_address)
        if normalized_email:
            address_hash = hashlib.sha1(normalized_email)
        else:
            address_hash = None
        address = self.create(email_address=email_address,address_hash=address_hash)
        return address


class EmailAddress(models.Model):
    id = UUIDField(primary_key=True, version=4)
    user_profile = models.ForeignKey(EmailProfile, null=True, blank=True)
    email_address = models.EmailField()
    date_added = models.DateTimeField(auto_now_add=True)
    address_hash = models.CharField(max_length=128, null=True, blank=True)
    objects = EmailAddressManager()

class ParsedEmailManager(models.Manager):
    @transaction.commit_manually
    def create_parsed_email(self, raw_message=None):
        msg = email.message_from_string(raw_message.content)
        parsed = self.create(
            raw_message=raw_message,
            message_id=msg.get('Message-ID',''),
            subject=msg.get('Subject','').lstrip().rstrip(),
        )

        if msg.is_multipart():
            content = u''
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    content = u'%s\n%s' % (content, unicode(part))
        else:
            content = msg.get_payload()
        parsed.content = content

        from_addresses = msg.get('From','').replace('\n', '').replace('\t', '').split(',')
        for each in from_addresses:
            try:
                parsed.from_email.add(EmailAddress.objects.get_or_create(each))
            except ValidationError:
                pass
        to_addresses = msg.get('To','').replace('\n', '').replace('\t', '').split(',')
        for each in to_addresses:
            try:
                parsed.to_email.add(EmailAddress.objects.get_or_create(each))
            except ValidationError:
                pass
        cc_addresses = msg.get('cc','').replace('\n', '').replace('\t', '').split(',')
        for each in cc_addresses:
            try:
                parsed.cc_email.add(EmailAddress.objects.get_or_create(each))
            except ValidationError:
                pass
        bcc_addresses = msg.get('Bcc','').replace('\n', '').replace('\t', '').split(',')
        for each in bcc_addresses:
            try:
                parsed.bcc_email.add(EmailAddress.objects.get_or_create(each))
            except ValidationError:
                pass
        parsed.save()
        raw_message.parsed = True
        raw_message.date_parsed = datetime.datetime.now()
        raw_message.save()
        transaction.commit()
class ParsedEmail(models.Model):
    id = UUIDField(primary_key=True, version=4)
    raw_message = models.ForeignKey(RawEmail)
    message_id = models.CharField(max_length=128, unique=True, blank=False, null=False)
    from_email = models.ManyToManyField(EmailAddress, related_name='from_addresses', null=True, blank=True)
    to_email = models.ManyToManyField(EmailAddress, related_name='to_addresses', null=True, blank=True)
    cc_email = models.ManyToManyField(EmailAddress, related_name='cc_addresses', null=True, blank=True)
    bcc_email = models.ManyToManyField(EmailAddress, related_name='bcc_addresses', null=True, blank=True)
    subject = models.CharField(max_length=256, null=True, blank=True)
    content = models.TextField(null=True,blank=True)

