from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from model_utils.models import TimeStampedModel, UUIDModel
from polymorphic.models import PolymorphicModel


class Node(UUIDModel, TimeStampedModel, PolymorphicModel):
    def __str__(self):
        return str(self.get_real_instance())

    def _is_group(self):
        return issubclass(self.get_real_instance().__class__, Group)

    @property
    def real_instance(self):
        real_instance = self.get_real_instance()
        if self._is_group():
            return real_instance._get_random_instance()
        return real_instance


class Group(Node):
    name = models.CharField(max_length=60, unique=True)
    nodes = models.ManyToManyField(Node, related_name="groups", blank=True)

    def _get_random_instance(self):
        return self.nodes.order_by("?").first()

    def __str__(self):
        return f"Group: {self.name}"


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
        # TODO: Refactor
        super().save(*args, **kwargs)
        real_event = self.get_real_instance()
        # group_ctype = ContentType.objects.get_for_model(Group)
        monitors = Monitor.objects.filter(
            Q(source=None)
            | Q(source=self.source)
            | (Q(source__group__isnull=False) & Q(source__group__nodes=self.source)),
            Q(target=None)
            | Q(target=self.target)
            | (Q(target__group__isnull=False) & Q(source__group__nodes=self.target)),
            event_type=real_event.polymorphic_ctype,
        )
        for monitor in monitors:
            for action in monitor.actions.all():
                if action.source:
                    source = action.source.real_instance
                else:
                    if (
                        real_event.source
                        and real_event.source_model == action.source_model
                    ):
                        source = real_event.source.real_instance
                    elif (
                        real_event.target
                        and real_event.target_model == action.source_model
                    ):
                        source = real_event.target.real_instance
                    else:
                        source = None
                if action.target:
                    target = action.target.real_instance
                else:
                    if (
                        real_event.target
                        and real_event.target_model == action.target_model
                    ):
                        target = real_event.target.real_instance
                    elif (
                        real_event.source
                        and real_event.source_model == action.target_model
                    ):
                        target = real_event.source.real_instance
                    else:
                        target = None
                action.execute(source, target)


class Monitor(Edge):
    event_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=~Q(app_label="core") & Q(model__endswith="event"),
    )

    def __str__(self):
        # TODO: Refactor
        event_name = self.event_type.name.title()
        if self.source and self.source._is_group():
            real_source = self.source.group.name
        else:
            real_source = self.source.real_instance if self.source else None
        if self.target and self.target._is_group():
            real_target = self.target.group.name
        else:
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
        raise NotImplementedError

    def get_target_queryset(self):
        raise NotImplementedError

    def execute(self, source: Node, target: Node):
        raise NotImplementedError
