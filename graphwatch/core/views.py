from dal import autocomplete
from django.contrib.contenttypes.models import ContentType

from .models import Node


class EventSourceSelect(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        """Customize the queryset for this class view"""

        if not self.request.user.is_authenticated:
            return Node.objects.none()

        event_ctype_id = self.forwarded.get("event_type", None)
        event_ctype = ContentType.objects.get(id=event_ctype_id)
        event_model = event_ctype.model_class()
        source_model = event_model.source_model
        queryset = Node.objects.instance_of(source_model)
        if self.q:
            queryset = list(
                filter(lambda n: self.q.lower() in str(n).lower(), queryset.all())
            )
        return queryset


class EventTargetSelect(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        """Customize the queryset for this class view"""

        if not self.request.user.is_authenticated:
            return Node.objects.none()

        event_ctype_id = self.forwarded.get("event_type", None)
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

        queryset = self.forwarded.get("source_qs", None)
        if self.q:
            queryset = list(
                filter(lambda n: self.q.lower() in str(n).lower(), queryset)
            )
        return queryset


class ActionTargetSelect(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        """Customize the queryset for this class view"""

        if not self.request.user.is_authenticated:
            return Node.objects.none()

        queryset = self.forwarded.get("target_qs", None)
        if self.q:
            queryset = list(
                filter(lambda n: self.q.lower() in str(n).lower(), queryset)
            )
        return queryset
