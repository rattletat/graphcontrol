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
def update_user_info(username):
    """Updates the account model with some additional information
    such as the Twitter user ID and bio"""
    account = Account.objects.get(username=username)
    handle = account.handle if hasattr(account, "handle") else Handle.get_random()
    user = get_user_object(handle, username=username)
    account.twitter_id = str(user.id)
    account.bio = user.description
    account.save()


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


@celery_app.task(max_retries=1)
def fetch_all_tweets():
    """Fetches the ten most recent tweets of every Twitter user and skips
    over private profiles (if they do not provide an account handle)"""
    for account in Account.objects.all():
        if account.twitter_id:
            handle = (
                account.handle if hasattr(account, "handle") else Handle.get_random()
            )
            try:
                tweets = get_user_tweets(handle, account.twitter_id)
                for tweet in tweets:
                    if not Tweet.objects.filter(twitter_id=tweet.id).exists():
                        Tweet(user=account, twitter_id=tweet.id, text=tweet.text).save()
            except tweepy_errors.Unauthorized:
                pass


@celery_app.task(max_retries=1)
def fetch_monitored_tweets():
    """Fetches the ten most recent tweets of monitored Twitter users"""
    for account in Account.objects.exclude(monitor__isnull=True):
        if account.twitter_id:
            handle = (
                account.handle if hasattr(account, "handle") else Handle.get_random()
            )
            try:
                tweets = get_user_tweets(handle, account.twitter_id)
                for tweet in tweets:
                    if not Tweet.objects.filter(twitter_id=tweet.id).exists():
                        Tweet(user=account, twitter_id=tweet.id, text=tweet.text).save()
            except tweepy_errors.Unauthorized:
                pass


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
