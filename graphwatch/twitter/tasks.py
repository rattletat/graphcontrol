from tweepy import errors as tweepy_errors

from config import celery_app

from .helpers import (
    determine_API_version,
    get_user_object,
    get_user_tweets,
    get_username,
    like_tweet,
)
from .models import Account, Handle, Tweet


@celery_app.task(max_retries=1)
def update_account(twitter_id=None, username=None):
    """Updates the account model with additional information"""
    if twitter_id:
        account = Account.objects.get(twitter_id=twitter_id)
    elif username:
        account = Account.objects.get(username=username)
    else:
        raise ValueError("Must specify twitter id or username")
    try:
        handle = account.handle if hasattr(account, "handle") else Handle.get_random()
        user = get_user_object(handle, twitter_id=twitter_id, username=username)
    except tweepy_errors.NotFound:
        account.delete()
    else:
        account.twitter_id = str(user.id)
        account.username = (
            user.username if hasattr(user, "username") else user.screen_name
        )
        account.name = user.name
        account.description = user.description
        account.save(refresh=False)


@celery_app.task(max_retries=1)
def validate_handle(handle_id):
    """Validates the handle data by determining and setting the
    corresponding API version and related user account"""
    handle = Handle.objects.get(id=handle_id)
    try:
        determine_API_version(handle)
    except tweepy_errors.Unauthorized:
        handle.verified = False
        handle.account = None
    else:
        username = get_username(handle)
        account, _ = Account.objects.get_or_create(username=username)
        handle.user = account
        handle.verified = True
    handle.save(refresh=False)


def fetch_tweets(accounts):
    """Fetches the ten most recent tweets of every provided Twitter user and skips
    over private profiles (if they do not provide an account handle)"""
    for account in accounts:
        if account.twitter_id:
            handle = (
                account.handle if hasattr(account, "handle") else Handle.get_random()
            )
            try:
                tweets = get_user_tweets(handle, account.twitter_id)
                for tweet in tweets:
                    if not Tweet.objects.filter(twitter_id=tweet.id).exists():
                        tweet = Tweet(
                            user=account,
                            twitter_id=tweet.id,
                            text=tweet.text,
                            created_at=tweet.created_at,
                        )
                        tweet.save()
                        yield tweet.twitter_id
            except tweepy_errors.Unauthorized:
                pass


@celery_app.task(max_retries=1)
def fetch_all_tweets():
    """Fetches the ten most recent tweets of all Twitter users.
    Returns list of fetched Tweet ids."""
    accounts = Account.objects.all()
    return list(fetch_tweets(accounts))


@celery_app.task(max_retries=1)
def fetch_monitored_tweets():
    """Fetches the ten most recent tweets of monitored Twitter users.
    Returns list of fetched Tweet ids."""
    accounts = Account.objects.exclude(monitors__isnull=True)
    fetch_tweets(accounts)


# ACTIONS
# ------------------------------------------------------------------


@celery_app.task(max_retries=1)
def like_tweet_by_random_bot(tweet_id):
    """Likes the specified tweet by a random bot.

    Note: The liking users endpoint limits you to a
    total of 100 liking accounts per tweet for all time.
    Additionally, the liked Tweets endpoint is also subject
    to the monthly Tweet cap applied at the Project level.
    """
    handle = Handle.get_random()
    like_tweet(handle, tweet_id)
