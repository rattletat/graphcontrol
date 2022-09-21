from config import celery_app

from ..helpers import follow_user, like_tweet, tweet_text, unfollow_user
from ..models import Account, Handle


@celery_app.task(name="Like Tweet", max_retries=1)
def like_tweet_task(account_id, tweet_id):
    """Likes the specified tweet by the specified account"""
    account = Account.objects.get(twitter_id=account_id)
    handle = account.handle
    like_tweet(handle, tweet_id)


@celery_app.task(name="Like Tweet By Random Bot", max_retries=1)
def like_tweet_by_random_bot(tweet_id):
    """Likes the specified tweet by a random bot.

    Note: The liking users endpoint limits you to a
    total of 100 liking accounts per tweet for all time.
    Additionally, the liked Tweets endpoint is also subject
    to the monthly Tweet cap applied at the Project level.
    """
    handle = Handle.get_random()
    like_tweet(handle, tweet_id)


@celery_app.task(name="Follow User", max_retries=1)
def follow_user_task(follower_id, following_id):
    """Follows the specified user"""
    account = Account.objects.get(twitter_id=follower_id)
    handle = account.handle
    follow_user(handle, following_id)


@celery_app.task(name="Unfollow User", max_retries=1)
def unfollow_user_task(follower_id, following_id):
    """Follows the specified user"""
    account = Account.objects.get(twitter_id=follower_id)
    handle = account.handle
    unfollow_user(handle, following_id)


@celery_app.task(name="Tweet Text", max_retries=1)
def tweet_text_task(account_id, text):
    """Tweets the specified text"""
    account = Account.objects.get(twitter_id=account_id)
    handle = account.handle
    tweet_text(handle, text)
