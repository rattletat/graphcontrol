import tweepy
from django.db import models, transaction
from django.template.defaultfilters import truncatechars
from model_utils.models import UUIDModel

from config import celery_app
from graphwatch.core.models import Node


class Account(Node):
    twitter_id = models.CharField(
        "Twitter ID", max_length=20, unique=True, null=True, default=None
    )
    username = models.CharField(unique=True, blank=False, max_length=15)
    name = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=200, blank=True)
    following = models.ManyToManyField(
        "self", related_name="followers", blank=True, symmetrical=False
    )

    def save(self, refresh=True, *args, **kwargs):
        if self._state.adding and refresh:
            transaction.on_commit(
                lambda: celery_app.send_task(
                    "Update Twitter Account",
                    kwargs={"username": self.username, "creation": self._state.adding},
                )
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

    def get_handle(self):
        if hasattr(self, "handle"):
            return self.handle
        else:
            return Handle.get_random()


class Handle(UUIDModel):
    class APIVersion(models.TextChoices):
        V1 = "V1", "Version 1"
        V2 = "V2", "Version 2"

    account = models.OneToOneField(
        Account, on_delete=models.CASCADE, null=True, blank=True
    )
    verified = models.BooleanField(default=False)
    api_version = models.CharField(
        "API Version", max_length=2, choices=APIVersion.choices, default=APIVersion.V1
    )

    api_key = models.CharField("API Key", max_length=25)
    api_key_secret = models.CharField("API Secret Key", max_length=50)
    access_token = models.CharField("API Access Token", max_length=50)
    access_token_secret = models.CharField("API Secret Access Token", max_length=50)

    @staticmethod
    def get_random():
        return Handle.objects.filter(verified=True).order_by("?").first()

    @property
    def api(self):
        if self.api_version == self.APIVersion.V1:
            auth = tweepy.OAuthHandler(self.api_key, self.api_key_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            return tweepy.API(auth, wait_on_rate_limit=True)
        elif self.api_version == self.APIVersion.V2:
            return tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_key_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True,
            )
        else:
            raise ValueError("Specified version invalid:", self.api_version)

    def save(self, refresh=True, *args, **kwargs):
        if refresh:
            transaction.on_commit(
                lambda: celery_app.send_task("Update Twitter Handle", [self.id])
            )
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("api_key", "access_token", "api_version")


class Tweet(Node):
    author = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="tweets")
    twitter_id = models.CharField(max_length=20, unique=True)
    text = models.CharField(max_length=600)
    created_at = models.DateTimeField()
    like_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Tweet by {self.author.username}: {truncatechars(self.text, 100)}"

    class Meta:
        ordering = ["-created_at"]
