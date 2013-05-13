from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = patterns('',
    url(r'^introductions/$', login_required(IntroductionListView.as_view())),
    url(r'^introductions/feedback/(?P<slug>\w+)$', FollowUpUpdate.as_view()),
    url(r'^introductions/(?P<slug>[\w-]+)$', login_required(IntroductionDetailView.as_view())),
    url(r'^introductions/(?P<slug>[\w-]+)/notify$', login_required(RequestFeedbackFormView.as_view())),
    url(r'^my/profile/?$', login_required(ProfileSettingsView.as_view())),
    )
