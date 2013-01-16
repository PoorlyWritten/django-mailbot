from django.contrib import admin
from models import RawEmail, ParsedEmail, EmailAddress
admin.site.register(RawEmail)
admin.site.register(ParsedEmail)
admin.site.register(EmailAddress)
