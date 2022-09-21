from tweepy import errors as tweepy_errors

from config import celery_app

from ..models import Account
from . import update

# @celery_app.task(max_retries=1)
# def fetch_unmonitored_tweets():
#     """Fetches the ten most recent tweets of all Twitter users.
#     Returns list of fetched Tweet ids."""
#     accounts = Account.objects.filter(monitors__isnull=True)
#     for account in accounts:
#         try:
#             update_tweets.delay(account.twitter_id)
#         except tweepy_errors.Unauthorized:
#             pass


# @celery_app.task(max_retries=1)
# def fetch_monitored_tweets():
#     """Fetches the ten most recent tweets of monitored Twitter users.
#     Returns list of fetched Tweet ids."""
#     accounts = Account.objects.filter(monitors__isnull=False)
#     for account in accounts:
#         try:
#             update_tweets.delay(account.twitter_id)
#         except tweepy_errors.Unauthorized:
#             pass


@celery_app.task(name="Fetch Random User Tweets", max_retries=1)
def fetch_random_user_tweets(count=100):
    """Fetches the hundred most recent tweets of a random Twitter user.
    Returns list of fetched Tweet ids."""
    random_account = Account.objects.order_by("?")[0]
    try:
        update.update_tweets.delay(random_account.twitter_id, count=count)
    except tweepy_errors.Unauthorized:
        pass


@celery_app.task(name="Fetch Random User Followers", max_retries=1)
def fetch_random_user_followers():
    """Fetches the hundred most recent tweets of a random Twitter user.
    Returns list of fetched Tweet ids."""
    random_account = Account.objects.order_by("?")[0]
    try:
        update.update_followers.delay(random_account.twitter_id)
    except tweepy_errors.Unauthorized:
        pass


@celery_app.task(name="Fetch Random User Following", max_retries=1)
def fetch_random_user_following():
    """Fetches the hundred most recent tweets of a random Twitter user.
    Returns list of fetched Tweet ids."""
    random_account = Account.objects.order_by("?")[0]
    try:
        update.update_following.delay(random_account.twitter_id)
    except tweepy_errors.Unauthorized:
        pass
