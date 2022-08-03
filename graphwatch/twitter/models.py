import tweepy
from django.core.validators import MinLengthValidator
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.template.defaultfilters import truncatechars
from model_utils.models import UUIDModel

from config import celery_app
from graphwatch.core.models import Node


class Account(Node):
    username = models.CharField(
        unique=True,
        max_length=15,
        validators=[MinLengthValidator(4)],
    )
    twitter_id = models.CharField(
        "Twitter ID", max_length=20, unique=True, null=True, default=None
    )
    description = models.CharField(max_length=200, null=True, default=None)

    def save(self, *args, **kwargs):
        if self._state.adding:
            transaction.on_commit(
                lambda: celery_app.send_task(
                    "graphwatch.twitter.tasks.update_user_info", [self.username]
                )
            )
        self.run_validators()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Twitter Account: {self.username}"

    def run_validators(self) -> None:
        for field_name, field_value in model_to_dict(self).items():
            model_field = getattr(Account, field_name)
            field = getattr(model_field, "field", object())
            validators = getattr(field, "validators", list())
            for validator_func in validators:
                if field_value is not None:
                    validator_func(field_value)


class Handle(UUIDModel):
    class APIVersion(models.TextChoices):
        V1 = "V1", "API Version 1"
        V2 = "V2", "API Version 2"

    user = models.OneToOneField(Account, on_delete=models.CASCADE, null=True)
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
        if self._state.adding or refresh:
            transaction.on_commit(
                lambda: celery_app.send_task(
                    "graphwatch.twitter.tasks.validate_handle", [self.id]
                )
            )
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("api_key", "access_token", "api_version")


class Tweet(Node):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    twitter_id = models.CharField(max_length=20, unique=True)
    text = models.CharField(max_length=600)

    def __str__(self):
        return f"Tweet by {self.user.username}: {truncatechars(self.text, 100)}"

    def save(self, *args, **kwargs):
        transaction.on_commit(
            lambda: self.user.dispatch_event("tweet_created", self.twitter_id)
        )
        super().save(*args, **kwargs)
