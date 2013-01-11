from django.forms import ModelForm
from .models import FollowUp

class FollowUpForm(ModelForm):
    class Meta:
        model = FollowUp
        fields = ('name', 'email', 'comment')
