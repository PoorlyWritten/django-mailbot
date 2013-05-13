import logging
logger = logging.getLogger(__name__)
from django import forms
from .models import FollowUp, IntroductionProfile

class FollowUpForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = ('name', 'email', 'comment')

class RequestFollowUpForm(forms.Form):
    introducee1_message = forms.CharField (widget=forms.widgets.Textarea(attrs={'rows':8,'cols':72}) )
    introducee2_message = forms.CharField (widget=forms.widgets.Textarea(attrs={'rows':8,'cols':72}) )
    include_introducee1 = forms.BooleanField(initial=True)
    include_introducee2 = forms.BooleanField(initial=True)


class IntroductionProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=64)
    last_name = forms.CharField(max_length=64)
    error_css_class = "error"
    class Meta:
        model = IntroductionProfile
        exclude = ('user',)

