import polymorphic.admin as polyadmin
from django.contrib import admin
from allauth.account import models as allauth_models
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as sites_models
from rest_framework.authtoken import models as rest_models

from .inlines import ActionInline

from ..forms import MonitorForm
from ..models import Monitor


@admin.register(Monitor)
class MonitorAdmin(polyadmin.PolymorphicInlineSupportMixin, admin.ModelAdmin):
    fields = ["event_type", "source", "target"]
    form = MonitorForm
    inlines = (ActionInline,)


admin.site.unregister(sites_models.Site)
admin.site.unregister(auth_models.Group)
admin.site.unregister(rest_models.TokenProxy)
admin.site.unregister(allauth_models.EmailAddress)
