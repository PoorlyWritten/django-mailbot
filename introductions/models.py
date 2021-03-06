import logging
logger = logging.getLogger(__name__)
import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models, IntegrityError, transaction
from django_extensions.db.fields import UUIDField
from email_integration.models import RawEmail, EmailAddress, TemplatedEmailMessage
from email_integration.send_mails import request_feedback_email
import os
import re

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
        return super(FollowUpManager, self).all().exclude(comment=None).order_by("-requested")

    def requested(self):
        return super(FollowUpManager, self).all().exclude(requested=None).order_by("-requested")

    def rated(self):
        return super(FollowUpManager, self).all().exclude(rating=None).order_by("-requested")


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
    rating = models.PositiveSmallIntegerField(default=75)
    recruiting = models.BooleanField(
            default=False
            )
    partnerships = models.BooleanField(
            default=False
            )
    sales = models.BooleanField(
            default=False
            )
    networking = models.BooleanField(
            default=False
            )
    fundrasing = models.BooleanField(
            default=False
            )
    mentorship = models.BooleanField(
            default=False
            )
    other = models.BooleanField(
            default=False
            )
    toosoon = models.BooleanField(
            default=False
            )
    objects = FollowUpManager()

    class Meta:
        unique_together = ('introduction', 'email')

    def __unicode__(self):
        return "Feedback from %s for %s" % (self.email, self.introduction)

    def request_feedback(self, msg=None):
        to_email = self.email
        connector_name = self.introduction.connector.get_full_name() or self.introduction.from_name
        from_email = "%s via intros.to <%s>" % (connector_name, settings.DEFAULT_FROM_EMAIL)
        other_email = self.other_email
        link = "http://intros.to/introductions/feedback/%s" % self.custom_url
        request_feedback_email(to_email, from_email, connector_name, other_email, msg, link)
        self.requested = datetime.datetime.utcnow()
        self.save()

    def comment_length(self):
        try:
            return len(self.comment)
        except TypeError:
            return 0


class IntroductionManager(models.Manager):
    @transaction.commit_on_success()
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
        last_sequence_dict = self.filter(connector=connector).aggregate(models.Max('sequence'))
        if last_sequence_dict['sequence__max']:
            sequence = last_sequence_dict['sequence__max'] + 1
        else:
            sequence = 1
        intro = Introduction(
            connector = connector,
            email_message = raw_email,
            subject = raw_email.subject,
            message = raw_email.payload,
            introducee1 = introducee1,
            introducee2 = introducee2,
            sequence = sequence
        )
        intro.save()
        logger.debug("Just created an introduction.  It's pk is : %s" % intro.pk)
        if connector.introductionpreferences.auto_send_feedback_requests:
            try:
                email = TemplatedEmailMessage.objects.get(name="IntroductionRegistered")
                email.send(to_email=connector.email, context_dict={'connector_name': connector.get_full_name(), 'introduction':intro })
            except Exception, error:
                pass
                logger.debug("Couldn't send mail announcing an intro made by %s because: %s" % ( connector, error))
        return intro

    def rated(self):
        pkset = set([x.introduction_id for x in FollowUp.objects.commented()])
        return super(IntroductionManager, self).filter(pk__in=pkset)

class Introduction(models.Model):
    id = UUIDField(primary_key=True, auto=True, version=4)
    connector = models.ForeignKey(User)
    introducee1 = models.EmailField()
    introducee2 = models.EmailField()
    subject = NullableCharField(max_length=128, null=True, blank=True)
    message = models.TextField()
    email_message = models.ForeignKey('email_integration.RawEmail', null=True, blank=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    sequence = models.IntegerField(default=None, null=True)
    objects = IntroductionManager()

    def get_absolute_url(self):
        return reverse('introduction_detail', args=[str(self.pk)])

    def get_user_url(self):
        return reverse('introduction_user_detail', args=[str(self.sequence)])


    @property
    def feedback_requested(self):
        if len(self.followup_set.requested()) > 0:
            return True
        return False

    @property
    def feedback_commented(self):
        if len(self.followup_set.commented()) > 0:
            return True
        return False

    def __unicode__(self):
        return u'%s introduced %s to %s' % (self.connector, self.introducee1, self.introducee2)

    @property
    def from_name(self):
       return self.email_message.sent_by_name

    @property
    def clean_message(self):
        replacer = re.compile("\n(From|Content-Type:)\ .*\n")
        return replacer.sub('\n',replacer.sub('\n',self.message)).lstrip("\n")

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


class IntroductionProfile(models.Model):
    user         = models.OneToOneField(User)
    location     = models.CharField(max_length=256, blank=True, null=True, default=None)
    headline     = models.CharField(max_length=256, blank=True, null=True, default=None)
    description  = models.CharField(max_length=256, blank=True, null=True, default=None)
    position  = models.CharField(max_length=256, blank=True, null=True, default=None)
    company  = models.CharField(max_length=256, blank=True, null=True, default=None)


class IntroductionPreferences(models.Model):
    user         = models.OneToOneField(User)
    send_gotcha_notifications = models.BooleanField(
            default=True,
            verbose_name="Send me a confirmation email when I bcc my@intros.to"
            )
    send_feedback_notifications = models.BooleanField(
            default=True,
            verbose_name="Notify me when someone leaves me feedback"
            )
    auto_send_feedback_requests = models.BooleanField(
            default=False,
            verbose_name="Automatically request feedback from people I've introduced"
            )
    send_monthly_summary = models.BooleanField(
            default=True,
            verbose_name="Send me a monthly summary of my intros and feedback"
            )


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

def create_introduction_profiles(sender, **kwargs):
    user = kwargs['instance']
    IntroductionProfile.objects.get_or_create(user=user)
    IntroductionPreferences.objects.get_or_create(user=user)


post_save.connect(create_introduction_profiles, sender=User)
#post_save.connect(test_signal_handler)
post_save.connect(parse_mail, sender=RawEmail)
