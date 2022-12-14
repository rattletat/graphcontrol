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
def fetch_random_user_tweets(limit=1000):
    """Fetches the thousand most recent tweets of a random Twitter user.
    Returns list of fetched Tweet ids."""
    random_account = Account.objects.order_by("?")[0]
    try:
        update.update_tweets.run(random_account.twitter_id, limit=limit)
    except tweepy_errors.Unauthorized:
        pass


@celery_app.task(name="Fetch Random User Followers", max_retries=1)
def fetch_random_user_followers(limit=1000):
    """Fetches the thousand most recent tweets of a random Twitter user.
    Returns list of fetched Tweet ids."""
    random_account = Account.objects.order_by("?")[0]
    try:
        update.update_followers.run(random_account.twitter_id, limit=limit)
    except tweepy_errors.Unauthorized:
        pass


@celery_app.task(name="Fetch Random User Following", max_retries=1)
def fetch_random_user_following(limit=1000):
    """Fetches the hundred most recent tweets of a random Twitter user.
    Returns list of fetched Tweet ids."""
    random_account = Account.objects.order_by("?")[0]
    try:
        update.update_following.run(random_account.twitter_id, limit=limit)
    except tweepy_errors.Unauthorized:
        pass


@celery_app.task(name="Fetch Oldest User Tweets", max_retries=1)
def fetch_oldest_user_tweets(limit=1000):
    """Fetches the thousand most recent tweets of the
    oldest real twitter user with zero tweets.
    Returns list of fetched Tweet ids."""
    oldest_account = (
        Account.objects.order_by("-created")
        .filter(tweets=None, handle__isnull=True, private=False)
        .first()
    )
    try:
        update.update_tweets.run(oldest_account.twitter_id, limit=limit)
    except tweepy_errors.Unauthorized:
        oldest_account.private = True
        oldest_account.save(refresh=False)


@celery_app.task(name="Fetch Oldest User Following", max_retries=1)
def fetch_oldest_user_following(limit=1000):
    """Fetches the thousand most recent follows of the
    oldest real twitter user with zero follows.
    Returns list of fetched Tweet ids."""
    oldest_account = (
        Account.objects.order_by("-created")
        .filter(following=None, handle__isnull=True, private=False)
        .first()
    )
    try:
        update.update_following.run(oldest_account.twitter_id, limit=limit)
    except tweepy_errors.Unauthorized:
        oldest_account.private = True
        oldest_account.save(refresh=False)


@celery_app.task(name="Fetch Oldest User Followers", max_retries=1)
def fetch_oldest_user_followers(limit=1000):
    """Fetches the thousand most recent followers of the
    oldest real twitter user with zero followers.
    Returns list of fetched Tweet ids."""
    oldest_account = (
        Account.objects.order_by("-created")
        .filter(following=None, handle__isnull=True, private=False)
        .first()
    )
    try:
        update.update_followers.run(oldest_account.twitter_id, limit=limit)
    except tweepy_errors.Unauthorized:
        oldest_account.private = True
        oldest_account.save(refresh=False)


@celery_app.task(name="Monitor User", max_retries=1)
def monitor_user(username):
    """Monitors user."""
    account = Account.objects.get(username=username)
    update.update_account(username=username)
    update.update_followers.run(twitter_id=account.twitter_id, limit=10)
    update.update_following.run(twitter_id=account.twitter_id, limit=10)
    update.update_tweets.run(twitter_id=account.twitter_id, limit=10)
