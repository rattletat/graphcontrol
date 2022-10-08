from dal import autocomplete
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from .models import Node


class MonitorSourceSelect(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        """Customize the queryset for this class view"""
        print(self.request)
        print(self.forwarded)
        event_ctype_id = self.forwarded.get("event_type", None)
        if not self.request.user.is_authenticated or not event_ctype_id:
            return Node.objects.none()
        event_ctype = ContentType.objects.get(id=event_ctype_id)
        event_model = event_ctype.model_class()
        queryset = Node.objects.filter(
            Q(instance_of=event_model.source_model) | Q(group__isnull=False)
        )
        if self.q:
            queryset = list(
                filter(lambda n: self.q.lower() in str(n).lower(), queryset.all())
            )
        return queryset


class MonitorTargetSelect(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        """Customize the queryset for this class view"""
        print(self.request)
        print(self.forwarded)
        event_ctype_id = self.forwarded.get("event_type", None)
        if not self.request.user.is_authenticated or not event_ctype_id:
            return Node.objects.none()

        event_ctype = ContentType.objects.get(id=event_ctype_id)
        event_model = event_ctype.model_class()
        queryset = Node.objects.filter(
            Q(instance_of=event_model.target_model) | Q(group__isnull=False)
        )
        if self.q:
            queryset = list(
                filter(lambda n: self.q.lower() in str(n).lower(), queryset.all())
            )
        return queryset


class ActionSourceSelect(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        action_ctype = self.forwarded.get("polymorphic_ctype", None)
        print(">>>>>>>>>>>>>>>>>>>>", action_ctype)
        if not self.request.user.is_authenticated or not action_ctype:
            return Node.objects.none()

        action_ctype = ContentType.objects.get(id=action_ctype)
        print(">>>>>>>>>>>>>>>>>>>>", action_ctype)
        action_model = action_ctype.model_class()
        print(">>>>>>>>>>>>>>>>>>>>", action_model)
        queryset = action_model.get_source_queryset() | Node.objects.filter(
            group__isnull=False
        )

        if self.q:
            queryset = list(
                filter(lambda n: self.q.lower() in str(n).lower(), queryset)
            )
        return queryset


class ActionTargetSelect(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        """Customize the queryset for this class view"""
        action_ctype = self.forwarded.get("polymorphic_ctype", None)
        print(self.request)
        print(self.forwarded)
        if not self.request.user.is_authenticated or not action_ctype:
            return Node.objects.none()

        action_ctype = ContentType.objects.get(id=action_ctype)
        action_model = action_ctype.model_class()
        queryset = action_model.get_target_queryset() | Node.objects.filter(
            group__isnull=False
        )
        if self.q:
            queryset = list(
                filter(lambda n: self.q.lower() in str(n).lower(), queryset)
            )
        return queryset
