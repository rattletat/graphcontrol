import math

import tweepy

from config import celery_app

from ..models import Handle, Stream, Tweet


@celery_app.task(
    name="Stream Tweets", max_retries=0, time_limit=math.inf, soft_time_limit=math.inf
)
def stream_tweets(stream_id):
    stream = Stream.objects.get(id=stream_id)
    if stream.handle.api_version == Handle.APIVersion.V1:

        class TweetStream(tweepy.Stream):
            def on_status(self, status):
                Tweet.create_from_status(status)

        tweet_stream = TweetStream(
            stream.handle.api_key,
            stream.handle.api_key_secret,
            stream.handle.access_token,
            stream.handle.access_token_secret,
        )
        while True:
            tweet_stream.filter(
                follow=[account.twitter_id for account in stream.group.nodes.all()]
            )
    else:
        raise NotImplementedError(
            "Tweet streaming using Twitter API V2 is not yet implemented!"
        )
