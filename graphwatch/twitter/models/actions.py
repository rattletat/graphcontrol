from config import celery_app
from graphwatch.core.models import Action

from ..models import Account, Tweet
from ..tasks import action


class TwitterAction(Action):
    pass


class LikeAction(TwitterAction):
    def get_source_queryset(self):
        return Account.objects.filter(handle__isnull=False).all()

    def get_target_queryset(self):
        return Tweet.objects.all()

    def execute(self):
        celery_app.send_task(
            action.like_tweet_task,
            kwargs={
                "account_id": self.source.twitter_id,
                "tweet_id": self.target.twitter_id,
            },
        )

    def __str__(self):
        return f"{self.source} likes {self.target}"


class FollowAction(TwitterAction):
    def get_source_queryset(self):
        return Account.objects.filter(handle__isnull=False)

    def get_target_queryset(self):
        return Account.objects.all()

    def execute(self):
        celery_app.send_task(
            action.follow_user_task,
            kwargs={
                "account_id": self.source.twitter_id,
                "tweet_id": self.target.twitter_id,
            },
        )

    def __str__(self):
        return f"{self.source} follows {self.target}"


class UnfollowAction(TwitterAction):
    def get_source_queryset(self):
        return Account.objects.filter(handle__isnull=False)

    def get_target_queryset(self):
        return Account.objects.all()

    def execute(self):
        celery_app.send_task(
            action.unfollow_user_task,
            kwargs={
                "account_id": self.source.twitter_id,
                "tweet_id": self.target.twitter_id,
            },
        )

    def __str__(self):
        return f"{self.source} unfollows {self.target}"
