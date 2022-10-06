from django.db.models.signals import post_save
from django.dispatch import receiver

from .models.events import TweetEvent
from .models.nodes import Tweet


@receiver(post_save, sender=Tweet, dispatch_uid="tweet_event")
def tweet_event(sender, instance, **kwargs):
    TweetEvent.objects.create(source=instance.author, target=instance)
