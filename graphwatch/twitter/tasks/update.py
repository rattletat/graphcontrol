import math
from collections.abc import Iterable

from tweepy import errors as tweepy_errors

from config import celery_app

from ..helpers import (
    determine_API_version,
    get_followers,
    get_following,
    get_user_object,
    get_user_tweets,
    get_username,
)
from ..models.events import (
    DescriptionChangeEvent,
    FollowEvent,
    NameChangeEvent,
    TweetEvent,
    UnfollowEvent,
    UsernameChangeEvent,
)
from ..models.nodes import Account, Handle, Tweet


@celery_app.task(name="Update Twitter Handle", max_retries=1)
def update_handle(handle_id):
    """Validates the handle data by determining and setting the
    corresponding API version and related user account"""
    handle = Handle.objects.get(id=handle_id)
    try:
        determine_API_version(handle)
    except tweepy_errors.Unauthorized:
        handle.verified = False
        handle.account = None
    else:
        handle.verified = True
        username = get_username(handle)
        account, _ = Account.objects.get_or_create(username=username)
        handle.account = account
    handle.save(refresh=False)


@celery_app.task(name="Update Twitter Account", max_retries=1)
def update_account(twitter_id=None, username=None, creation=False):
    """Updates the account model with additional information"""
    if twitter_id:
        account = Account.objects.get(twitter_id=twitter_id)
    elif username:
        account = Account.objects.get(username=username)
    else:
        raise ValueError("Must specify twitter id or username")
    try:
        user = get_user_object(
            account.get_handle(), twitter_id=twitter_id, username=username
        )
    except tweepy_errors.NotFound:
        account.delete()
    else:
        account.twitter_id = str(user.id)
        username = user.username if hasattr(user, "username") else user.screen_name
        if account.username != username:
            account.username = username
            if not creation:
                UsernameChangeEvent.objects.create(source=account, target=account)
        if account.name != user.name:
            account.name = user.name
            if not creation:
                NameChangeEvent.objects.create(source=account, target=account)
        if account.description != user.description:
            account.description = user.description
            if not creation:
                DescriptionChangeEvent.objects.create(source=account, target=account)
        account.save(refresh=False)


@celery_app.task(name="Update Recent Tweets", max_retries=1)
def update_tweets(twitter_id, limit=math.inf):
    """Fetches the `count` most recent tweets of the specified account."""
    account = Account.objects.get(twitter_id=twitter_id)
    tweets = get_user_tweets(account.get_handle(), twitter_id, limit=limit)
    for tweet in tweets:
        if not Tweet.objects.filter(twitter_id=tweet["id"]).exists():
            tweet = Tweet.objects.create(
                author=account,
                twitter_id=tweet["id"],
                text=tweet["text"],
                created_at=tweet["created_at"],
                like_count=tweet["like_count"],
            )
            TweetEvent.objects.create(source=account, target=tweet)
        else:
            tweet_instance = Tweet.objects.get(twitter_id=tweet["id"])
            tweet_instance.like_count = tweet["like_count"]


def _get_accounts(user_data):
    for user in user_data:
        if not Account.objects.filter(twitter_id=user["twitter_id"]).exists():
            account = Account(**user)
            account.save(refresh=False)
        else:
            account = Account.objects.get(twitter_id=user["twitter_id"])
        yield account


def _add_follows(edges: Iterable[tuple[Account, Account]]):
    for source, target in edges:
        source.following.add(target)
        FollowEvent.objects.create(source=source, target=target)


def _del_follows(edges: Iterable[tuple[Account, Account]]):
    for source, target in edges:
        source.following.remove(target)
        UnfollowEvent.objects.create(source=source, target=target)


@celery_app.task(name="Update Twitter Follows", max_retries=1)
def update_following(twitter_id, limit=math.inf):
    """Creates and updates the users the specified account is following."""
    account = Account.objects.get(twitter_id=twitter_id)
    old_follows = set(account.following.all())
    new_follows = set(
        _get_accounts(get_following(account.get_handle(), twitter_id, limit=limit))
    )

    _add_follows((account, follow) for follow in new_follows - old_follows)
    _del_follows((account, follow) for follow in old_follows - new_follows)


@celery_app.task(name="Update Twitter Followers", max_retries=1)
def update_followers(twitter_id, limit=math.inf):
    """Creates and updates users who are followers of the specified account."""
    account = Account.objects.get(twitter_id=twitter_id)
    old_followers = set(account.followers.all())
    new_followers = set(
        _get_accounts(get_followers(account.get_handle(), twitter_id, limit=limit))
    )

    _add_follows((follower, account) for follower in new_followers - old_followers)
    _del_follows((follower, account) for follower in old_followers - new_followers)
