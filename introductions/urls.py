from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = patterns('',
    url(r'^$', login_required(IntroductionListView.as_view())),
    url(r'feedback/(?P<slug>\w+)$', FollowUpUpdate.as_view()),
    url(r'^(?P<slug>[\w-]+)$', login_required(IntroductionDetailView.as_view())),
    url(r'^(?P<slug>[\w-]+)/notify$', login_required(IntroductionNotificationRequestView.as_view())),
    )
