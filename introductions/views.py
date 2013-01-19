import logging
logger = logging.getLogger(__name__)
from django.views.generic import ListView, UpdateView, DetailView
from .models import Introduction, FollowUp
from .forms import FollowUpForm
from email_bot.views import OLContextMixin

class IntroductionListView(OLContextMixin, ListView):
    #model = Introduction
    heading = "Track your introductions"

    def get_queryset(self):
        logger.debug("Returning filtered introductions made by %s" % self.request.user)
        return Introduction.objects.filter(connector = self.request.user)

class IntroductionDetailView(OLContextMixin, DetailView):
    model = Introduction
    slug_field='id'

    def get_queryset(self):
        logger.debug("Returning filtered introductions made by %s" % self.request.user)
        return Introduction.objects.filter(connector = self.request.user)

class IntroductionNotificationRequestView(OLContextMixin, DetailView):
    template_name = 'introduction/notify.html'
    heading = "Email Requests Sent!"
    model = Introduction
    slug_field='id'

    def get_queryset(self):
        logger.debug("Returning filtered introductions made by %s" % self.request.user)
        return Introduction.objects.filter(connector = self.request.user)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.create_followups()
        for each in self.object.followup_set.all():
            try:
                logger.debug("About to ask for the email to be sent")
                each.request_feedback()
            except Exception, e:
                logger.debug("Couldn't send feedback request because: %s" % e)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)




class FollowUpUpdate(OLContextMixin, UpdateView):
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
        logger.debug("logged as debug in valid")
        return super(FollowUpUpdate, self).form_valid(form)
