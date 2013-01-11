import logging
logger = logging.getLogger(__name__)
from django.views.generic import ListView, UpdateView
from .models import Introduction, FollowUp
from .forms import FollowUpForm

class IntroductionDetailMixin(object):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IntroductionDetailMixin, self).get_context_data(**kwargs)
        try:
            logger.debug(self.__dict__)
        except:
            pass
        logger.debug("context=%s" % context)
        return context

class IntroductionList(ListView):
    model = Introduction

class FollowUpUpdate(UpdateView):
    model = FollowUp
    form_class = FollowUpForm
    slug_field = 'custom_url'
    success_url = "/introductions"

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
