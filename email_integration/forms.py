from django import forms
from .models import EmailAddress
from send_mails import send_verification_email
import datetime

class VerifyEmailForm(forms.Form):
    email = forms.EmailField()

    def send_email(self):
        email_address, created =  EmailAddress.objects.get_or_create_email(
            self.cleaned_data['email'])
        send_verification_email(self.cleaned_data['email'],email_address.verification_hash)
        email_address.verification_email_sent = datetime.datetime.utcnow()
        email_address.save()
