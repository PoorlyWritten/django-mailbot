import logging
logger = logging.getLogger(__name__)
from django.contrib import admin
from models import RawEmail, EmailAddress, EmailProfile
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


admin.site.register(RawEmail, RawEmailAdmin)
admin.site.register(EmailAddress)
admin.site.register(EmailProfile)
