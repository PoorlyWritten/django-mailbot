import logging
logger = logging.getLogger(__name__)
from django.contrib import admin
from .models import (
    EmailAddress,
    EmailProfile,
    EmailWhitelist,
    RawEmail,
    TemplatedEmailMessage,
)
from introductions.models import Introduction
import datetime

def parse_messages(modeladmin, request, queryset):
    for each in queryset:
        try:
            Introduction.objects.create_introduction(each)
            each.parsed =True
            each.date_parsed = datetime.datetime.utcnow()
            each.save()
        except Exception, error:
            logger.debug('There was a problem creating an introduction from %s : %s ' % (each, error))
            pass
parse_messages.short_description= "Parse each of the marked messages"

class RawEmailAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'date_added', 'parsed')
    actions = [parse_messages]
    def id(self):
        return self.pk

class EmailProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__email', 'user__first_name', 'user__last_name' ]
    #list_display = ('user__first_name', 'user_last_name', 'user__username', 'user__email', 'date_added')

class EmailAddressAdmin(admin.ModelAdmin):
    search_fields = ['email_address', 'full_name' ]

admin.site.register(RawEmail, RawEmailAdmin)
admin.site.register(EmailAddress, EmailAddressAdmin)
admin.site.register(EmailProfile, EmailProfileAdmin)
admin.site.register(TemplatedEmailMessage)
admin.site.register(EmailWhitelist)
