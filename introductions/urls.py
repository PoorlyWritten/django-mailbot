from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
    url(r'^$', IntroductionList.as_view()),
    url(r'feedback/(?P<slug>\w+)$', FollowUpUpdate.as_view()),
    )
