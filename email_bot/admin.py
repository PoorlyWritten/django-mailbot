import logging
logger = logging.getLogger(__name__)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from introductions.models import Introduction

class MyUserAdmin(UserAdmin):
    list_display = ('email', 'intros_registered', 'username', 'first_name', 'last_name', 'date_joined', 'is_active', 'is_staff')
    list_editable = ('first_name', 'last_name', 'username')
    ordering = ('-date_joined',)

    def intros_registered(self, instance, *args, **kwargs):
        return len(Introduction.objects.filter(connector=instance))

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
