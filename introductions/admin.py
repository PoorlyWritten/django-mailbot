import logging
logger = logging.getLogger(__name__)
from django.contrib import admin
from models import Introduction, FollowUp

def create_followups(modeladmin, request, queryset):
    for each in queryset:
        try:
            each.create_followups()
        except Exception, error:
            logger.debug("There was an error creating followups for %s : %s" % (each, error))
create_followups.short_description = "Force the creation of the followups"

class IntroductionAdmin(admin.ModelAdmin):
    actions = [create_followups]


admin.site.register(Introduction, IntroductionAdmin)
admin.site.register(FollowUp)
