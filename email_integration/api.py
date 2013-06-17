from tastypie.resources import ModelResource
from .models import RawEmail, EmailAddress, EmailProfile


class EmailAddressResource(ModelResource):
    class Meta:
        queryset = EmailAddress.objects.all()
        always_return_data = True
        list_allowed_methods = []

class EmailProfileResource(ModelResource):
    class Meta:
        queryset = EmailProfile.objects.all()
        always_return_data = True
        list_allowed_methods = []


class RawEmailResource(ModelResource):
    class Meta:
        queryset = RawEmail.objects.all()
        always_return_data = True
        list_allowed_methods = []
