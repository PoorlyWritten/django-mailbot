import logging
logger = logging.getLogger(__name__)
from django.views.generic import ListView, UpdateView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from .models import Introduction, FollowUp
from .forms import FollowUpForm, RequestFollowUpForm, IntroductionProfileForm
from email_bot.views import OLContextMixin
from email_integration.models import TemplatedEmailMessage
from email_integration.views import ProtectedViewMixin
from django.template import Template, Context

class IntroductionListView(ProtectedViewMixin, OLContextMixin, ListView):
    #model = Introduction
    heading = "Track your introductions"

    def get_queryset(self):
        logger.debug("Returning filtered introductions made by %s" % self.request.user)
        return Introduction.objects.filter(connector = self.request.user).order_by('-created')


class IntroductionDetailView(ProtectedViewMixin, OLContextMixin, DetailView):
    model = Introduction
    slug_field='id'

    def get_queryset(self):
        logger.debug("Returning filtered introductions made by %s" % self.request.user)
        return Introduction.objects.filter(connector = self.request.user)


class IntroductionNotificationRequestView(ProtectedViewMixin, OLContextMixin, DetailView):
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


class RequestFeedbackFormView(ProtectedViewMixin, OLContextMixin, SingleObjectMixin, FormView):
    template_name = 'introductions/notify.html'
    heading = "Email Requests Sent!"
    model = Introduction
    form_class = RequestFollowUpForm
    slug_field='id'

    def get_initial(self):
        try:
            assert self.object
        except AttributeError:
            self.object = self.get_object()
        msg_template = TemplatedEmailMessage.objects.get(name="RequestFeedback")
        initial_message1 = Template(msg_template.text_content).render(Context(
            { 'connector_name': self.object.connector.get_full_name,
              'other_email': self.object.introducee2,
             }
        ))
        initial_message2 = Template(msg_template.text_content).render(Context(
            { 'connector_name': self.object.connector.get_full_name,
              'other_email': self.object.introducee1,
             }
        ))
        return dict(
            introducee1_message = initial_message1,
            introducee2_message = initial_message2,
        )

    def get_success_url(self):
        try:
            assert self.object
        except AttributeError:
            self.object = self.get_object()
        return "/introductions/%s#FeedbackRequested" % self.object.pk

    def get_context_data(self, **kwargs):
        return super(RequestFeedbackFormView, self).get_context_data(object=self.object, **kwargs)


    def form_invalid(self, form):
        logger.debug("logged as debug in invalid")
        logger.debug("form errors = %s" % form.errors)
        return super(RequestFeedbackFormView, self).form_invalid(form)

    def form_valid(self, form):
        logger.debug("logged as debug in valid")
        try:
            assert self.object
        except AttributeError:
            self.object = self.get_object()
        self.object.create_followups()
        for each in self.object.followup_set.all():
            if form.cleaned_data['include_introducee1'] and self.object.introducee1 == each.email:
                try:
                    logger.debug("About to ask for the email to be sent")
                    each.request_feedback(msg=form.cleaned_data['introducee1_message'])
                except Exception, e:
                    logger.debug("Couldn't send feedback request because: %s" % e)
            if form.cleaned_data['include_introducee2'] and self.object.introducee2 == each.email:
                try:
                    logger.debug("About to ask for the email to be sent")
                    each.request_feedback(msg=form.cleaned_data['introducee2_message'])
                except Exception, e:
                    logger.debug("Couldn't send feedback request because: %s" % e)
        return super(RequestFeedbackFormView, self).form_valid(form)


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
        try:
            assert self.object
        except AttributeError:
            self.object = self.get_object()
        email = TemplatedEmailMessage.objects.get(name='NewFeedback')
        email.send(to_email=self.object.introduction.connector.email, context_dict={
            'connector_name': self.object.introduction.connector.get_full_name(),
            'email': self.object.email,
            'other_email': self.object.other_email,
            'introduction': self.object.introduction,
        })
        return super(FollowUpUpdate, self).form_valid(form)



class ProfileSettingsView(FormView):
    template_name = "settings.html"
    form_class = IntroductionProfileForm

    def get_initial(self):
        initial = super(ProfileSettingsView, self).get_initial()
        initial.update({
            'first_name' : self.request.user.first_name,
            'last_name' : self.request.user.last_name,
        })
        return initial

    def form_valid(self, form):
        self.request.user.first_name  = form.cleaned_data['first_name']
        self.request.user.last_name  = form.cleaned_data['last_name']
        self.request.user.save()
        return super(ProfileSettingsView, self).form_valid(form)




