import logging
logger = logging.getLogger(__name__)
from django.views.generic import TemplateView

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
                context['my_addrs'] = self.request.user.emailprofile_set.all()[0].emailaddress_set.all()
                logger.debug('%s' % context['my_addrs'])
            except:
                pass
        return context

class OLTemplateView(OLContextMixin, TemplateView):
    pass
