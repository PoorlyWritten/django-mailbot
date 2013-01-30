import logging
logger = logging.getLogger(__name__)
from django import forms
from .models import FollowUp

class FollowUpForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = ('name', 'email', 'comment')

class RequestFollowUpForm(forms.Form):
    #introducee1_message = forms.CharField (widget=forms.widgets.Textarea(attrs={'rows':6,'cols':72}) )
    #introducee2_message = forms.CharField (widget=forms.widgets.Textarea(attrs={'rows':6,'cols':72}) )
    introducee1_message = forms.CharField (widget=forms.HiddenInput)
    introducee2_message = forms.CharField (widget=forms.HiddenInput)
    send_introducee1 = forms.BooleanField(initial=True, widget=forms.HiddenInput)
    send_introducee2 = forms.BooleanField(initial=True, widget=forms.HiddenInput)

    def request_feedback(self, obj):
        obj.create_followups()
        for each in obj.followup_set.all():
            try:
                logger.debug("About to ask for the email to be sent")
                each.request_feedback()
            except Exception, e:
                logger.debug("Couldn't send feedback request because: %s" % e)
