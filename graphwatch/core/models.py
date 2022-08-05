from django.db import models
from model_utils.models import TimeStampedModel, UUIDModel
from polymorphic.models import PolymorphicModel

from config import celery_app


class Node(UUIDModel, TimeStampedModel, PolymorphicModel):
    def dispatch_event(self, event, node_id=None):
        monitors = Monitor.objects.filter(node=self, event=event)
        for monitor in monitors:
            celery_app.send_task(monitor.action, [node_id])


# class Action(UUIDModel):
#     name = models.CharField(max_length=100)
#     source = models.TextField(blank=True)


# class Event(UUIDModel, TimeStampedModel, PolymorphicModel):
#     created = models.DateTimeField(editable=False)

#     def save(self, *args, **kwargs):
#         """On save, update timestamps"""
#         if not self.id:
#             self.created = timezone.now()
#         return super(Event, self).save(*args, **kwargs)


class Monitor(UUIDModel):
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="monitors")
    event = models.CharField(max_length=256, blank=True, null=True)
    action = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return f"Monitor( Node={self.node.account}, Event={self.event}, Action={self.action} )"
