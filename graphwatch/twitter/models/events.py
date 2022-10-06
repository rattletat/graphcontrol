from graphwatch.core.models import Event

from .nodes import Account, Tweet


class TwitterEvent(Event):
    pass


class TweetEvent(TwitterEvent):
    source_model = Account
    target_model = Tweet

    def __str__(self):
        return f'{self.source} tweets "{self.target.real_instance.text}"'


class FollowEvent(TwitterEvent):
    source_model = Account
    target_model = Account

    def __str__(self):
        return f"{self.source} follows {self.target}"


class UnfollowEvent(TwitterEvent):
    source_model = Account
    target_model = Account

    def __str__(self):
        return f"{self.source} unfollows {self.target}"


class UsernameChangeEvent(TwitterEvent):
    source_model = Account

    def __str__(self):
        return f"{self.source} updates username to {self.source.account.username}"


class NameChangeEvent(TwitterEvent):
    source_model = Account

    def __str__(self):
        return f"{self.source} updates name {self.source}"


class DescriptionChangeEvent(TwitterEvent):
    source_model = Account

    def __str__(self):
        return f'{self.source} updates description "{self.source.account.description}"'
