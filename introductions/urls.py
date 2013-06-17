from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from .views import *
from .api import *

introduction_resource = IntroductionResource()

urlpatterns = patterns('',
        #url(r'^introductions/?$', login_required(IntroductionListView.as_view())),
    url(r'^dashboard/?$', login_required(IntroductionListView.as_view(template_name="dashboard.html")), name='introduction_dashboard'),
    url(r'^introductions?/followup/(?P<slug>\w+)$', FollowUpUpdate.as_view(template_name="introductions/followup_form.html")),
    url(r'^introductions?/feedback/(?P<slug>\w+)$', FollowUpUpdate.as_view(template_name="introductions/feedback_form.html")),
    url(r'^introductions?/(?P<slug>[\w-]+)$', login_required(IntroductionDetailView.as_view()), name='introduction_detail'),
    url(r'^my/introductions?/(?P<slug>[\w-]+)$', login_required(IntroductionUserDetailView.as_view()), name='introduction_user_detail'),
    url(r'^my/introduction/(?P<slug>[\w-]+)/notify$', login_required(RequestFeedbackFormView.as_view())),
    url(r'^my/profile/?$', login_required(ProfileSettingsView.as_view()), name='introduction_settings'),
    url(r'^my/settings/?$', login_required(ProfilePreferencesView.as_view(template_name="notifications.html")), name='introduction_preferences'),
    url(r'^api/', include(introduction_resource.urls)),
    )
