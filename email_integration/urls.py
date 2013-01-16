
from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
    url(r'verify$', VerifyEmailFormView.as_view()),
    url(r'verify/(?P<slug>\w+)$', VerifyEmailView.as_view()),
    )
