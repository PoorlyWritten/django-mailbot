from django.conf.urls import patterns, include, url
from django.contrib.auth.views import logout_then_login
from email_bot.views import OLTemplateView

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
    url(r'', include('email_integration.urls')),
    (r'^browserid/', include('django_browserid.urls')),
    (r'^avatar/', include('avatar.urls')),
    (r'^$', OLTemplateView.as_view(template_name="home.html")),
    (r'^pricing$', OLTemplateView.as_view(template_name="pricing.html")),
    (r'^dev/introductions$', OLTemplateView.as_view(template_name="introduction.html")),
    (r'^dev/main$', OLTemplateView.as_view(template_name="main.html")),
    (r'^logout$', logout_then_login),
)

