import helpers

from config import celery_app

from ..models import Account


@celery_app.task(name="Like Tweet", max_retries=1)
def like_task(account_id, tweet_id):
    """Likes the specified tweet by the specified account"""
    account = Account.objects.get(twitter_id=account_id)
    handle = account.handle
    helpers.like(handle, tweet_id)


# @celery_app.task(name="Like Tweet By Random Bot", max_retries=1)
# def like_tweet_by_random_bot(tweet_id):
#     """Likes the specified tweet by a random bot.

#     Note: The liking users endpoint limits you to a
#     total of 100 liking accounts per tweet for all time.
#     Additionally, the liked Tweets endpoint is also subject
#     to the monthly Tweet cap applied at the Project level.
#     """
#     handle = Handle.get_random()
#     helpers.like(handle, tweet_id)


@celery_app.task(name="Follow User", max_retries=1)
def follow_user_task(follower_id, following_id):
    """Follows the specified user"""
    account = Account.objects.get(twitter_id=follower_id)
    handle = account.handle
    helpers.follow(handle, following_id)


@celery_app.task(name="Unfollow User", max_retries=1)
def unfollow_user_task(follower_id, following_id):
    """Follows the specified user"""
    account = Account.objects.get(twitter_id=follower_id)
    handle = account.handle
    helpers.unfollow(handle, following_id)


@celery_app.task(name="Tweet Text", max_retries=1)
def tweet_task(account_id, text):
    """Tweets the specified text"""
    account = Account.objects.get(twitter_id=account_id)
    handle = account.handle
    helpers.tweet(handle, text)


@celery_app.task(name="Retweet Tweet", max_retries=1)
def retweet_task(account_id, tweet_id):
    """Tweets the specified text"""
    account = Account.objects.get(twitter_id=account_id)
    handle = account.handle
    helpers.retweet(handle, tweet_id)
