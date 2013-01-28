import logging
logger = logging.getLogger(__name__)
from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django_extensions.db.fields import UUIDField
from email_integration.send_mails import request_feedback_email
from email_integration.models import RawEmail, EmailAddress
from djangoratings.fields import AnonymousRatingField
import datetime
import os

class NullableCharField(models.CharField):
    description = "CharField that obeys null=True"

    def get_db_prep_value(self, value, *args, **kwargs):
        my_value = super(NullableCharField, self).get_db_prep_value(value, *args, **kwargs)
        return my_value or None


    def to_python(self, value):
        if isinstance(value, models.CharField):
            return value
        return value or ""

    def get_internal_type(self):
        return "CharField"

    def south_field_triple(self):
        "Returns a suitable description of this field for South"
        # We'll just introspect ourselves, since we inherit.
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.CharField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)


class FollowUpManager(models.Manager):
    def commented(self):
        return super(FollowUpManager, self).all().exclude(comment=None)

class FollowUp(models.Model):
    id = UUIDField(primary_key=True, auto=True, version=4)
    name = NullableCharField(max_length=128, null=True)
    email = models.EmailField(max_length=128, null=True)
    other_email = models.EmailField(max_length=128, null=True)
    user = models.ForeignKey(User, null=True)
    introduction = models.ForeignKey('Introduction', editable=False)
    created = models.DateTimeField(auto_now_add=True)
    custom_url = NullableCharField(max_length=64, unique=True, null=True)
    comment = models.TextField(null=True,blank=True)
    requested = models.DateTimeField(null=True, blank=True)
    added = models.DateTimeField(auto_now=True)
    rating = AnonymousRatingField(range=10)
    objects = FollowUpManager()

    class Meta:
        unique_together = ('introduction', 'email')

    def __unicode__(self):
        return "Feedback from %s for %s" % (self.email, self.introduction)

    def request_feedback(self):
        to_email = self.email
        connector_name = self.introduction.connector.get_full_name() or self.introduction.from_name
        link = "http://introduction.es/introductions/feedback/%s" % self.custom_url
        request_feedback_email(to_email, connector_name, link)
        self.requested = datetime.datetime.utcnow()
        self.save()


class IntroductionManager(models.Manager):
    def create_introduction(self, raw_email):
        from_email = raw_email.isolated_from_addr
        connector = None
        try:
            connector = User.objects.get(email=from_email)
        except User.DoesNotExist:
            pass
        if not connector:
            try:
                connector = EmailAddress.objects.get(email_address=from_email).user_profile.user
            except (EmailAddress.DoesNotExist, AttributeError):
                pass
        if not connector:
            # This came from an unregistered user
            # TODO: Send welcome email and invite to join
            print "Can't find a registered user to be the connector for this new message.  From was: %s" % from_email
            return None
        introducee1 = None
        introducee2 = None
        recipients = []
        recipients.extend(raw_email.isolated_to)
        recipients.extend(raw_email.isolated_cc)
        for each in recipients:
            if each != raw_email.isolated_delivered_to:
                if not introducee1:
                    introducee1 = each
                    continue
                if not introducee2:
                    introducee2 = each
                    continue
        intro = Introduction(
            connector = connector,
            email_message = raw_email,
            subject = raw_email.subject,
            message = raw_email.payload,
            introducee1 = introducee1,
            introducee2 = introducee2
        )
        intro.save()
        logger.debug("Just created an introduction.  It's pk is : %s" % intro.pk)
        return intro



class Introduction(models.Model):
    id = UUIDField(primary_key=True, auto=True, version=4)
    connector = models.ForeignKey(User)
    introducee1 = models.EmailField()
    introducee2 = models.EmailField()
    subject = NullableCharField(max_length=128, null=True, blank=True)
    message = models.TextField()
    email_message = models.ForeignKey('email_integration.RawEmail', null=True, blank=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    objects = IntroductionManager()

    def __unicode__(self):
        return u'%s introduced %s to %s' % (self.connector, self.introducee1, self.introducee2)

    @property
    def from_name(self):
       return self.email_message.sent_by_name

    def create_followups(self):
        followup1 = FollowUp(
            email=self.introducee1,
            other_email=self.introducee2,
            introduction=self,
            custom_url=os.urandom(32).encode('hex')
        )
        try:
            followup1.save()
        except IntegrityError:
            pass
        followup2 = FollowUp(
            email=self.introducee2,
            other_email=self.introducee1,
            introduction=self,
            custom_url=os.urandom(32).encode('hex')
        )
        try:
            followup2.save()
        except IntegrityError:
            pass

def parse_one_mail(raw_message_id):
    logger.debug("parse_one_mail was called...")
    print "parse_one_mail was called..."
    raw_message=RawEmail.objects.get(pk=raw_message_id)
    print "Raw Message = %s " % raw_message.pk
    try:
        intro = Introduction.objects.create_introduction(raw_email = raw_message)
        raw_message.date_parsed = datetime.datetime.utcnow()
        raw_message.parsed = True
        raw_message.save()
        return intro
    except IntegrityError,e:
        logger.debug("couldn't create an introduction because: %s" % e)
        return None

def create_followups(intro_pk):
    logger.debug("create_followups was called...")
    try:
        intro = Introduction.objects.get(pk=intro_pk)
        intro.create_followups()
    except Introduction.DoesNotExist:
        pass


from django.db.models.signals import post_save

def parse_mail(sender,**kwargs):
    #{'raw': False, 'instance': <RawEmail: raw email received at 2013-01-15 15:37:39+00:00>, 'signal': <django.dispatch.dispatcher.Signal object at 0x34dd350>, 'using': 'default', 'created': False}
    instance = kwargs['instance']
    logger.debug("In parse_mail where instance.pk = %s" % instance.pk)
    if not instance.parsed:
        intro = parse_one_mail(instance.pk)
        if intro:
            intro.create_followups()
            intro.save()

def test_signal_handler(sender, **kwargs):
    logger.debug('test_signal_handler - kwargs = %s' % kwargs)
    print 'test_signal_handler - kwargs = %s' % kwargs
    logger.debug('test_signal_handler - sender = %s' % sender)
    print 'test_signal_handler - sender = %s' % sender
    logger.debug('test_signal_handler - instance = %s' % kwargs['instance'])
    print 'test_signal_handler - instance = %s' % kwargs['instance']
    logger.debug('test_signal_handler - instance.__dict__ = %s' % kwargs['instance'].__dict__)
    print 'test_signal_handler - instance.__dict__ = %s' % kwargs['instance'].__dict__

#post_save.connect(test_signal_handler)
post_save.connect(parse_mail, sender=RawEmail)
