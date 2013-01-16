import logging
logger = logging.getLogger(__name__)
from django.views.generic import ListView, UpdateView
from .models import Introduction, FollowUp
from .forms import FollowUpForm

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
        return context

class IntroductionList(OLContextMixin, ListView):
    #ParsedEmail.objects.filter(from_email__user_profile__user__id = me.id)
    model = Introduction
    heading = "Track your introductions"

    def get_queryset(self):
        return Introduction.objects.filter(connector = self.request.user)


class FollowUpUpdate(UpdateView, OLContextMixin):
    model = FollowUp
    form_class = FollowUpForm
    slug_field = 'custom_url'
    success_url = "/introductions"
    heading = "How did it go?"

    def get_object(self,queryset=None):
        logger.debug("In get_object")
        return super(FollowUpUpdate, self).get_object(queryset=queryset)

    def form_invalid(self, form):
        logger.debug("logged as debug in invalid")
        logger.debug("form errors = %s" % form.errors)
        return super(FollowUpUpdate, self).form_invalid(form)

    def form_valid(self, form):
        logger.debug("logged as debug in invalid")
        return super(FollowUpUpdate, self).form_valid(form)
