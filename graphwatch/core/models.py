from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from model_utils.models import TimeStampedModel, UUIDModel
from polymorphic.models import PolymorphicModel


class Node(UUIDModel, TimeStampedModel, PolymorphicModel):
    def __str__(self):
        return str(self.get_real_instance())


class Edge(UUIDModel, TimeStampedModel, PolymorphicModel):
    source = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="outgoing_edges",
    )
    target = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="incoming_edges",
    )


class Event(Edge):
    source_model = None
    target_model = None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        real_event = self.get_real_instance()
        monitors = Monitor.objects.filter(
            Q(event_source=None) | Q(event_source=self.source),
            Q(event_target=None) | Q(event_source=self.target),
            event_type=real_event.polymorphic_ctype,
        )
        for monitor in monitors:
            for action in monitor.actions:
                action.execute()


class Monitor(UUIDModel):
    event_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=~Q(app_label="core") & Q(model__endswith="event"),
    )
    event_source = models.ForeignKey(
        Node,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="outgoing_monitors",
    )
    event_target = models.ForeignKey(
        Node,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="incoming_monitors",
    )

    def __str__(self):
        event_name = self.event_type.name.title()
        real_source = (
            self.event_source.get_real_instance() if self.event_source else None
        )
        real_target = (
            self.event_target.get_real_instance() if self.event_target else None
        )
        if self.event_source and self.event_target:
            return f"{event_name}: {real_source} -> {real_target}"
        if self.event_source:
            return f"{event_name}: {real_source}"
        if self.event_target:
            return f"{event_name}: {real_target}"
        return f"{event_name}"


class Action(Edge):
    monitor = models.ForeignKey(
        Monitor,
        on_delete=models.CASCADE,
    )
    source_qs = []
    target_qs = []
