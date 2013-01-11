from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.auth.views import logout_then_login

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'oneleap_email_bot.views.home', name='home'),
    # url(r'^oneleap_email_bot/', include('oneleap_email_bot.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^introductions/', include('introductions.urls')),
    (r'^browserid/', include('django_browserid.urls')),
    (r'^index/', TemplateView.as_view(template_name="index.html")),
#    (r'^feedback/', TemplateView.as_view(template_name="feedback.html")),
    (r'^home/', TemplateView.as_view(template_name="home.html")),
    (r'^logout$', logout_then_login),
)

