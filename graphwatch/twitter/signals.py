from django.db.models.signals import post_save
from django.dispatch import receiver

from graphwatch.core.models import Monitor

from .models import Tweet


@receiver(post_save, sender=Tweet)
def tweet_event_dispatcher(sender, instance, created, **kwargs):
    if created:
        monitors = Monitor.objects.filter(
            node=instance, action=Monitor.Events.TWEET_EVENT
        ).all()
        for monitor in monitors:
            monitor.activate()
