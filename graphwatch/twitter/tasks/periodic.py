from tweepy import errors as tweepy_errors

from config import celery_app

from ..models import Account
from .update import update_tweets


@celery_app.task(max_retries=1)
def fetch_unmonitored_tweets():
    """Fetches the ten most recent tweets of all Twitter users.
    Returns list of fetched Tweet ids."""
    accounts = Account.objects.filter(monitors__isnull=True)
    for account in accounts:
        try:
            update_tweets.delay(account.twitter_id)
        except tweepy_errors.Unauthorized:
            pass


@celery_app.task(max_retries=1)
def fetch_monitored_tweets():
    """Fetches the ten most recent tweets of monitored Twitter users.
    Returns list of fetched Tweet ids."""
    accounts = Account.objects.filter(monitors__isnull=False)
    for account in accounts:
        try:
            update_tweets.delay(account.twitter_id)
        except tweepy_errors.Unauthorized:
            pass
