import logging
logger = logging.getLogger(__name__)
from django import forms
from .models import FollowUp, IntroductionProfile, IntroductionPreferences

class RangeInput(forms.widgets.Input):
    """HTML5 Range Input"""
    input_type = 'range'


class FollowUpForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = ('comment',
                  'rating',
                  'recruiting',
                  'partnerships',
                  'sales',
                  'networking',
                  'fundrasing',
                  'mentorship',
                  'other',
                  'toosoon')
        widgets = {
            'rating': forms.widgets.HiddenInput(),
            }

class RequestFollowUpForm(forms.Form):
    introducee1_message = forms.CharField (widget=forms.widgets.HiddenInput())
    introducee2_message = forms.CharField (widget=forms.widgets.HiddenInput())
    include_introducee1 = forms.BooleanField(initial=True)
    include_introducee2 = forms.BooleanField(initial=True)


class IntroductionProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=64)
    last_name = forms.CharField(max_length=64)
    error_css_class = "error"
    required_css_class = "required"

    class Meta:
        model = IntroductionProfile
        exclude = ('user',)
        fields = [
                'first_name',
                'last_name',
                'location',
        ]

class IntroductionPreferenceForm(forms.ModelForm):
    error_css_class = "error"
    required_css_class = "required"
    class Meta:
        model = IntroductionPreferences
        exclude = ('user',)
