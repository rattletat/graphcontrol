from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from model_utils.models import TimeStampedModel, UUIDModel
from polymorphic.models import PolymorphicModel


class Node(UUIDModel, TimeStampedModel, PolymorphicModel):
    def __str__(self):
        return str(self.get_real_instance())

    @property
    def real_instance(self):
        return self.get_real_instance()


class Edge(UUIDModel, TimeStampedModel, PolymorphicModel):
    source = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="outgoing_edges",
        null=True,
        blank=True,
    )
    target = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="incoming_edges",
        null=True,
        blank=True,
    )


class Event(Edge):
    source_model = None
    target_model = None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        real_event = self.get_real_instance()
        monitors = Monitor.objects.filter(
            Q(source=None) | Q(source=self.source),
            Q(target=None) | Q(source=self.target),
            event_type=real_event.polymorphic_ctype,
        )
        for monitor in monitors:
            for action in monitor.actions.all():
                action.execute()


class Monitor(Edge):
    # TODO: Use event foreignkey instead of this
    event_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=~Q(app_label="core") & Q(model__endswith="event"),
    )

    def __str__(self):
        # TODO: Make more expressive
        event_name = self.event_type.name.title()
        real_source = self.source.real_instance if self.source else None
        real_target = self.target.real_instance if self.target else None
        if self.source and self.target:
            return f"{event_name}: {real_source} -> {real_target}"
        if self.source:
            return f"{event_name}: {real_source}"
        if self.target:
            return f"{event_name}: {real_target}"
        return f"{event_name}"


class Action(Edge):
    event_monitor = models.ForeignKey(
        Monitor,
        on_delete=models.CASCADE,
        related_name="actions",
    )

    def get_source_queryset(self):
        # return Node.objects.none()
        raise NotImplementedError

    def get_target_queryset(self):
        # return Node.objects.none()
        raise NotImplementedError
