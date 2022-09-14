from allauth.account.models import EmailAddress
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline
from rest_framework.authtoken.models import TokenProxy

from graphwatch.twitter.admin import inlines as twitter_inlines

from .models import Action, Monitor


class ActionInline(StackedPolymorphicInline):
    model = Action
    child_inlines = twitter_inlines.ACTION_INLINES


@admin.register(Monitor)
class MonitorAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    inlines = (ActionInline,)


admin.site.unregister(Site)
admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
admin.site.unregister(EmailAddress)
