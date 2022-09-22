from dal import autocomplete
from django.contrib.contenttypes.models import ContentType

from graphwatch.twitter.models import Account

from .models import Node


class MonitorSourceSelect(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        """Customize the queryset for this class view"""

        event_ctype_id = self.forwarded.get("event_type", None)
        if not self.request.user.is_authenticated or not event_ctype_id:
            return Node.objects.none()
        event_ctype = ContentType.objects.get(id=event_ctype_id)
        event_model = event_ctype.model_class()
        source_model = event_model.source_model
        queryset = Node.objects.instance_of(source_model)
        if self.q:
            queryset = list(
                filter(lambda n: self.q.lower() in str(n).lower(), queryset.all())
            )
        return queryset


class MonitorTargetSelect(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        """Customize the queryset for this class view"""

        event_ctype_id = self.forwarded.get("event_type", None)
        if not self.request.user.is_authenticated or not event_ctype_id:
            return Node.objects.none()

        event_ctype = ContentType.objects.get(id=event_ctype_id)
        event_model = event_ctype.model_class()
        target_model = event_model.target_model
        queryset = Node.objects.instance_of(target_model)
        if self.q:
            queryset = list(
                filter(lambda n: self.q.lower() in str(n).lower(), queryset.all())
            )
        return queryset


class ActionSourceSelect(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Node.objects.none()

        queryset = Account.objects.filter(handle__isnull=False).all()
        if self.q:
            queryset = list(
                filter(lambda n: self.q.lower() in str(n).lower(), queryset)
            )
        return queryset


class ActionTargetSelect(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        """Customize the queryset for this class view"""
        print("Target alive")
        print(self.request)
        print(self.forwarded)

        if not self.request.user.is_authenticated:
            return Node.objects.none()

        queryset = Account.objects.all()
        if self.q:
            queryset = list(
                filter(lambda n: self.q.lower() in str(n).lower(), queryset)
            )
        return queryset
