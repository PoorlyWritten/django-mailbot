import logging
logger = logging.getLogger(__name__)
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from .forms import VerifyEmailForm
from .models import EmailAddress, EmailProfile


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


class VerifyEmailFormView(OLContextMixin, FormView):
    form_class = VerifyEmailForm
    template_name = 'verify_form.html'
    success_url = '/introductions'
    heading = "Verify a new email address"

    def form_valid(self, form):
        form.send_email()
        return super(VerifyEmailFormView, self).form_valid(form)

class VerifyEmailView(OLContextMixin, DetailView):
    model = EmailAddress
    slug_field = 'verification_hash'
    queryset = EmailAddress.objects.filter(verification_complete=False)
    heading = "Gotcha!"

    def get(self, request, *args, **kwargs):
        if not request.user:
            return None
        self.object = self.get_object()
        self.object.user_profile, created = EmailProfile.objects.get_or_create(user=request.user)
        self.object.verification_complete = True
        self.object.save()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)





