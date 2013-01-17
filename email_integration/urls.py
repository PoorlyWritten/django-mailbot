from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = patterns('',
    url(r'verify$', login_required(VerifyEmailFormView.as_view())),
    url(r'verify/(?P<slug>\w+)$', login_required(VerifyEmailView.as_view())),
    )
