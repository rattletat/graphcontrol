from django.db import models

from graphwatch.core.models import Action, Node

from ..models import Account, Tweet
from ..tasks import action


class TwitterAction(Action):
    pass


class LikeAction(TwitterAction):
    source_model = Account
    target_model = Tweet

    @staticmethod
    def get_source_queryset():
        return Node.objects.instance_of(Account).filter(account__handle__isnull=False)

    @staticmethod
    def get_target_queryset():
        return Node.objects.instance_of(Tweet)

    def execute(self, source, target):
        action.like_tweet_task.apply_async(
            kwargs={
                "account_id": source.twitter_id,
                "tweet_id": target.twitter_id,
            },
        )

    def __str__(self):
        source = self.source.real_instance if self.source else "______"
        target = self.target.real_instance if self.target else "______"
        return f"{source} likes {target}"


class FollowAction(TwitterAction):
    source_model = Account
    target_model = Account

    @staticmethod
    def get_source_queryset():
        return Node.objects.instance_of(Account).filter(account__handle__isnull=False)

    @staticmethod
    def get_target_queryset():
        return Node.objects.instance_of(Account)

    def execute(self, source, target):
        action.follow_user_task.apply_async(
            kwargs={
                "follower_id": source.twitter_id,
                "following_id": target.twitter_id,
            },
        )

    def __str__(self):
        source = self.source.real_instance if self.source else "______"
        target = self.target.real_instance if self.target else "______"
        return f"{source} follows {target}"


class UnfollowAction(TwitterAction):
    source_model = Account
    target_model = Account

    @staticmethod
    def get_source_queryset():
        return Node.objects.instance_of(Account).filter(account__handle__isnull=False)

    @staticmethod
    def get_target_queryset():
        return Node.objects.instance_of(Account)

    def execute(self, source, target):
        action.unfollow_user_task.apply_async(
            kwargs={
                "follower_id": source.twitter_id,
                "following_id": target.twitter_id,
            },
        )

    def __str__(self):
        source = self.source.real_instance if self.source else "______"
        target = self.target.real_instance if self.target else "______"
        return f"{source} unfollows {target}"


class TweetAction(TwitterAction):
    source_model = Account
    target_model = Tweet
    text = models.CharField("Tweet text", max_length=280)

    @staticmethod
    def get_source_queryset():
        return Node.objects.instance_of(Account).filter(account__handle__isnull=False)

    @staticmethod
    def get_target_queryset():
        return Node.objects.none()

    def execute(self, source, target):
        action.tweet_text_task.apply_async(
            kwargs={
                "account_id": source.twitter_id,
                "text": self.text,
            },
        )

    def __str__(self):
        source = self.source.real_instance if self.source else "______"
        return f"{source} tweets '{self.text}'"
