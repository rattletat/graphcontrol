from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from graphwatch.twitter.models import Account

from .models import Monitor

ACTIONS = ["graphwatch.twitter.tasks.like_tweet_by_random_bot"]
EVENTS = ["tweet_created"]


class MonitorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["node"].queryset = Account.objects.all()

    class Meta:
        model = Monitor
        widgets = {
            "event": forms.Select(
                choices=[(event, event) for event in EVENTS],
                attrs={"class": "form-control"},
            ),
            "action": forms.Select(
                choices=[(action, action) for action in ACTIONS],
                attrs={"class": "form-control"},
            ),
        }
        fields = "__all__"


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    form = MonitorForm

    def get_queryset(self, request):
        twitter_account_content_type = ContentType.objects.get_for_model(Account)
        return (
            super()
            .get_queryset(request)
            .filter(node__polymorphic_ctype=twitter_account_content_type)
        )

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "node":
    #         kwargs["node"] = Account.objects.all()
    #     return super(MonitorAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
