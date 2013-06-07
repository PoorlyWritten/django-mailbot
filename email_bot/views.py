import logging
logger = logging.getLogger(__name__)
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect

class OLContextMixin(object):
    """
    A default context mixin that passes the keyword arguments received by
    get_context_data as the template context.
    """

    def get_context_data(self, **kwargs):
        context = super(OLContextMixin, self).get_context_data(**kwargs)
        try:
            context['heading'] = self.heading
            logger.debug("Adding heading to context")
        except AttributeError:
            pass
        if self.request.user.is_authenticated:
            try:
                context['my_addrs'] = self.request.user.emailprofile.emailaddress_set.all()
                logger.debug('myaddrs = %s' % context['my_addrs'])
            except:
                logger.debug("Something went wrong trying to add the myaddrs thing")
                pass
        return context

class OLTemplateView(OLContextMixin, TemplateView):
    pass


class OLHomeView(OLTemplateView):
    def dispatch(self, request, *args, **kwargs):
        logger.debug("In home dispatch where %s.anon = %s and %s.auth = %s" % (
            request.user,
            request.user.is_anonymous(),
            request.user,
            request.user.is_authenticated()))
        if request.user.is_authenticated() and request.user.emailprofile.is_approved:
            return HttpResponseRedirect('/introductions')
        else:
            return super(OLHomeView, self).dispatch(request, *args, **kwargs)
