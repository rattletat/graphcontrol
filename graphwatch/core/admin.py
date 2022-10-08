import polymorphic.admin as polyadmin
from allauth.account.models import EmailAddress
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from rest_framework.authtoken.models import TokenProxy

from graphwatch.twitter.admin import inlines as twitter_inlines

from .forms import MonitorForm
from .models import Action, Monitor


class ActionInline(polyadmin.StackedPolymorphicInline):
    model = Action
    child_inlines = twitter_inlines.ACTION_INLINES
    fk_name = "event_monitor"


@admin.register(Monitor)
class MonitorAdmin(polyadmin.PolymorphicInlineSupportMixin, admin.ModelAdmin):
    fields = ["event_type", "source", "target"]
    form = MonitorForm
    inlines = (ActionInline,)


admin.site.unregister(Site)
admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
admin.site.unregister(EmailAddress)
