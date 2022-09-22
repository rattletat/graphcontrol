from django.db import models

from graphwatch.core.models import Action

from ..models import Account, Tweet
from ..tasks import action


class TwitterAction(Action):
    pass


class LikeAction(TwitterAction):
    @staticmethod
    def get_source_queryset():
        return Account.objects.filter(handle__isnull=False)

    @staticmethod
    def get_target_queryset():
        return Tweet.objects

    def execute(self):
        action.like_tweet_task.apply_async(
            kwargs={
                "account_id": self.source.real_instance.twitter_id,
                "tweet_id": self.target.real_instance.twitter_id,
            },
        )

    def __str__(self):
        return f"{self.source.real_instance} likes {self.target.real_instance}"


class FollowAction(TwitterAction):
    @staticmethod
    def get_source_queryset():
        return Account.objects.filter(handle__isnull=False)

    @staticmethod
    def get_target_queryset():
        return Account.objects

    def execute(self):
        action.follow_user_task.apply_async(
            kwargs={
                "follower_id": self.source.real_instance.twitter_id,
                "following_id": self.target.real_instance.twitter_id,
            },
        )

    def __str__(self):
        return f"{self.source.real_instance} follows {self.target.real_instance}"


class UnfollowAction(TwitterAction):
    @staticmethod
    def get_source_queryset():
        return Account.objects.filter(handle__isnull=False)

    @staticmethod
    def get_target_queryset():
        return Account.objects

    def execute(self):
        action.unfollow_user_task.apply_async(
            kwargs={
                "follower_id": self.source.real_instance.twitter_id,
                "following_id": self.target.real_instance.twitter_id,
            },
        )

    def __str__(self):
        return f"{self.source.real_instance} unfollows {self.target.real_instance}"


class TweetAction(TwitterAction):
    text = models.CharField("Tweet text", max_length=280)

    @staticmethod
    def get_source_queryset():
        return Account.objects.filter(handle__isnull=False)

    @staticmethod
    def get_target_queryset():
        return Account.objects.none()

    def execute(self):
        action.unfollow_user_task.apply_async(
            kwargs={
                "follower_id": self.source.real_instance.twitter_id,
                "following_id": self.target.real_instance.twitter_id,
            },
        )

    def __str__(self):
        return f'{self.source.real_instance} tweets "{self.text}"'
