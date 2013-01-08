from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.fields import UUIDField

# Create your models here.
class Introduction(models.Model):
    id = UUIDField(primary_key=True, version=4)
    email_message = models.ForeignKey('ParsedEmail', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

class FollowUp(models.Model):
    id = UUIDField(primary_key=True, version=4)
    user = models.ForeignKey(User)
    introduction = models.ForeignKey(Introduction)
    created = models.DateTimeField(auto_now_add=True)
    custom_url = models.CharField(max_length=64)
    comment = models.TextField(null=True,blank=True)
    requested = models.DateTimeField(null=True, blank=True)
    added = models.DateTimeField(null=True, blank=True)
