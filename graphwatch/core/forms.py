from django import forms

from config import celery_app
from graphwatch.twitter.models import Account

from .models import Monitor


class MonitorForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["action"] = forms.ModelChoiceField(queryset=celery_app.tasks.keys())
        if self.fields["node"] and self.fields["node"].instance_of(Account):
            self.fields["events"] = forms.ModelChoiceField(queryset=["tweet_creation"])

    class Meta:
        model = Monitor
