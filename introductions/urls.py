from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from .views import *
from .api import *

introduction_resource = IntroductionResource()

urlpatterns = patterns('',
    url(r'^introductions/?$', login_required(IntroductionListView.as_view())),
    url(r'^dashboard/?$', login_required(IntroductionListView.as_view(template_name="dashboard.html"))),
    url(r'^introductions/feedback/(?P<slug>\w+)$', FollowUpUpdate.as_view()),
    url(r'^introductions/(?P<slug>[\w-]+)$', login_required(IntroductionDetailView.as_view())),
    url(r'^introductions/(?P<slug>[\w-]+)/notify$', login_required(RequestFeedbackFormView.as_view())),
    url(r'^my/profile/?$', login_required(ProfileSettingsView.as_view())),
    url(r'^my/settings/?$', login_required(ProfilePreferencesView.as_view())),
    url(r'^api/', include(introduction_resource.urls)),
    )
