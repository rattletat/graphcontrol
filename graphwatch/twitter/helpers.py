import tweepy
import tweepy.errors as tweepy_errors


def determine_API_version(handle):
    """Sets the handle to the right API Version by testing out two calls."""
    try:
        handle.api_version = handle.APIVersion.V2
        get_user_id(handle)
    except tweepy_errors.Forbidden:
        handle.api_version = handle.APIVersion.V1
        get_user_id(handle)


def get_user_tweets(
    handle, user_id, tweet_fields=["created_at", "public_metrics"], count=10
):
    """Returns the ten most recent tweets of a specified user"""
    if handle.api_version == handle.APIVersion.V1:
        tweets = handle.api.user_timeline(user_id=user_id, count=count)
    elif handle.api_version == handle.APIVersion.V2:
        tweets = handle.api.get_users_tweets(
            id=user_id, tweet_fields=tweet_fields, user_auth=True
        ).data
    else:
        raise ValueError("Specified version invalid:", handle.api_version)
    return [
        {
            "id": str(tweet.id),
            "text": tweet.text,
            "created_at": tweet.created_at,
            "like_count": tweet.favorite_count
            if hasattr(tweet, "favorite_count")
            else tweet.public_metrics["like_count"],
        }
        for tweet in tweets
    ]


def get_user_object(handle, username=None, twitter_id=None, fields=["description"]):
    """Returns the Twitter user object of the handle account
    Note: This object is different depending on whether API V1 or V2 is used"""
    if username and handle.api_version == handle.APIVersion.V1:
        return handle.api.get_user(screen_name=username)
    elif twitter_id and handle.api_version == handle.APIVersion.V1:
        return handle.api.get_user(id=twitter_id)
    elif username and handle.api_version == handle.APIVersion.V2:
        return handle.api.get_user(
            username=username, user_fields=fields, user_auth=True
        ).data
    elif twitter_id and handle.api_version == handle.APIVersion.V2:
        return handle.api.get_user(
            id=twitter_id, user_fields=fields, user_auth=True
        ).data
    else:
        raise ValueError(
            "Not provided identifer or specified version invalid:", handle.api_version
        )


def get_username(handle):
    """Returns the Twitter username of the handle account"""
    if handle.api_version == handle.APIVersion.V1:
        return handle.api.verify_credentials().screen_name
    elif handle.api_version == handle.APIVersion.V2:
        return handle.api.get_me(user_auth=True).data.username
    else:
        raise ValueError("Specified version invalid:", handle.api_version)


def get_user_id(handle):
    """Returns the Twitter ID of the handle account"""
    if handle.api_version == handle.APIVersion.V1:
        return str(handle.api.verify_credentials().id)
    elif handle.api_version == handle.APIVersion.V2:
        return str(handle.api.get_me(user_auth=True).data.id)
    else:
        raise ValueError("Specified version invalid:", handle.api_version)


def like_tweet(handle, tweet_id):
    """Likes the specified tweet using the handle account"""
    if handle.api_version == handle.APIVersion.V1:
        return handle.api.create_favorite(tweet_id)
    elif handle.api_version == handle.APIVersion.V2:
        return handle.api.like(tweet_id, user_auth=True)
    else:
        raise ValueError("Specified version invalid:", handle.api_version)


def get_following(handle, user_id):
    """Returns a list of users the specified user ID is following."""
    if handle.api_version == handle.APIVersion.V1:
        data = list(
            tweepy.Cursor(
                handle.api.get_friends,
                user_id=user_id,
                include_user_entities=False,
                skip_status=True,
                count=200,
            ).items()
        )
    elif handle.api_version == handle.APIVersion.V2:
        data = list(
            tweepy.Paginator(
                handle.api.get_users_following,
                id=user_id,
                user_fields=["description"],
                max_results=1000,
                user_auth=True,
            ).flatten()
        )
    else:
        raise ValueError("Specified version invalid:", handle.api_version)

    return [
        {
            "twitter_id": str(user.id),
            "username": user.username
            if hasattr(user, "username")
            else user.screen_name,
            "name": user.name,
            "description": user.description,
        }
        for user in data
    ]


def get_followers(handle, user_id):
    """Returns a list of users who are followers of the specified user."""
    if handle.api_version == handle.APIVersion.V1:
        data = list(
            tweepy.Cursor(
                handle.api.get_followers,
                user_id=user_id,
                include_user_entities=False,
                skip_status=True,
                count=200,
            ).items()
        )
    elif handle.api_version == handle.APIVersion.V2:
        data = list(
            tweepy.Paginator(
                handle.api.get_users_followers,
                id=user_id,
                user_fields=["description"],
                max_results=1000,
                user_auth=True,
            ).flatten()
        )
    else:
        raise ValueError("Specified version invalid:", handle.api_version)

    return [
        {
            "twitter_id": str(user.id),
            "username": user.username
            if hasattr(user, "username")
            else user.screen_name,
            "name": user.name,
            "description": user.description,
        }
        for user in data
    ]


def follow_user(handle, user_id):
    """Follows the specified tweet using the handle account"""
    if handle.api_version == handle.APIVersion.V1:
        return handle.api.create_friendship(user_id=user_id)
    elif handle.api_version == handle.APIVersion.V2:
        return handle.api.follow_user(user_id=user_id, user_auth=True)
    else:
        raise ValueError("Specified version invalid:", handle.api_version)


def unfollow_user(handle, user_id):
    """Unfollows the specified tweet using the handle account"""
    if handle.api_version == handle.APIVersion.V1:
        return handle.api.destroy_friendship(user_id=user_id)
    elif handle.api_version == handle.APIVersion.V2:
        return handle.api.unfollow_user(user_id=user_id, user_auth=True)
    else:
        raise ValueError("Specified version invalid:", handle.api_version)
