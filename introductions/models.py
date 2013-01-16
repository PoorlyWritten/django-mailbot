import logging
logger = logging.getLogger(__name__)
from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.fields import UUIDField
import random

def gen_short_url(length):
    digits = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz'
    return ''.join([digits[random.randint(0,len(digits))] for x in range(0,length)])


class NullableCharField(models.CharField):
    description = "CharField that obeys null=True"

    def get_db_prep_value(self, value, *args, **kwargs):
        my_value = super(NullableCharField, self).get_db_prep_value(value, *args, **kwargs)
        return my_value or None


    def to_python(self, value):
        if isinstance(value, models.CharField):
            return value
        return value or ""


class FollowUpManager(models.Manager):
    def create_followup(self,**kwargs):
        if 'custom_url' not in kwargs:
            url_candidates = []
            for x in range(1,10):
                for x in range(1,10):
                    url_candidates.append(gen_short_url(random.randint(5,12)))
                found = [x.custom_url for x in self.filter(custom_url__in=url_candidates)]
                candidates = set(url_candidates).symmetric_difference(set(found))
                if len(candidates) > 0:
                    kwargs['custom_url'] = candidates[0]
                    return self.create(**kwargs)
            return None # This is statistically improbable
        return self.create(**kwargs)


class FollowUp(models.Model):
    id = UUIDField(primary_key=True, version=4)
    name = NullableCharField(max_length=128, null=True)
    email = models.EmailField(max_length=128, null=True)
    other_email = models.EmailField(max_length=128, null=True)
    user = models.ForeignKey(User, null=True)
    introduction = models.ForeignKey('Introduction', editable=False)
    created = models.DateTimeField(auto_now_add=True)
    custom_url = NullableCharField(max_length=64, unique=True, null=True)
    comment = models.TextField(null=True,blank=True)
    requested = models.DateTimeField(null=True, blank=True)
    added = models.DateTimeField(null=True, blank=True)
    objects = FollowUpManager()

    class Meta:
        unique_together = ('introduction', 'email')

    def __unicode__(self):
        return "Feedback from %s for %s" % (self.email, self.introduction)

class IntroductionManager(models.Manager):
    def create_from_parsedmail(self, parsed_mail):
        intro = Introduction(email_message = parsed_mail,
            connector = parsed_mail.from_email.all()[0].user_profile.user,
            subject = parsed_mail.subject,
            message = parsed_mail.content,
                             )
        introducee1 = None
        introducee2 = None
        recipients = []
        recipients.extend(parsed_mail.to_email.all())
        recipients.extend(parsed_mail.cc_email.all())
        for each in recipients:
            if each.email_address != parsed_mail.delivered_to:
                if not introducee1:
                    introducee1 = each
                    continue
                if not introducee2:
                    introducee2 = each
                    continue
        intro.introducee1 = introducee1
        intro.introducee2 = introducee2
        intro.save()

        #ParsedEmail.objects.filter(from_email__user_profile__user__id = me.id)



class Introduction(models.Model):
    id = UUIDField(primary_key=True, version=4)
    connector = models.ForeignKey(User)
    introducee1 = models.EmailField()
    introducee2 = models.EmailField()
    subject = NullableCharField(max_length=128, null=True, blank=True)
    message = models.TextField()
    email_message = models.ForeignKey('email_integration.ParsedEmail', null=True, blank=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    objects = IntroductionManager()

    def __unicode__(self):
        return u'%s introduced %s to %s' % (self.connector, self.introducee1, self.introducee2)

    def create_followups(self):
        try:
            FollowUp.objects.create_followup(email=self.introducee1, other_email=self.introducee2, introduction=self)
        except Exception, error:
            logger.debug(error)
            pass
        try:
            FollowUp.objects.create_followup(email=self.introducee2, other_email=self.introducee1, introduction=self)
        except Exception, error:
            logger.debug(error)
            pass


