import tweepy.errors as tweepy_errors


def determine_API_version(handle):
    """Sets the handle to the right API Version by testing out two calls."""
    try:
        handle.api_version = handle.APIVersion.V2
        get_user_id(handle)
    except tweepy_errors.Forbidden:
        handle.api_version = handle.APIVersion.V1
        get_user_id(handle)


def get_user_tweets(handle, user_id):
    """Returns the ten most recent tweets of a specified user"""
    if handle.api_version == handle.APIVersion.V1:
        return handle.api.user_timeline(user_id=user_id, count=10)
    elif handle.api_version == handle.APIVersion.V2:
        return handle.api.get_users_tweets(id=user_id, user_auth=True).data
    else:
        raise ValueError("Specified version invalid:", handle.api_version)


def get_user_object(handle, username, fields=["description"]):
    """Returns the Twitter user object of the handle account
    Note: This object is different depending on whether API V1 or V2 is used"""
    if handle.api_version == handle.APIVersion.V1:
        return handle.api.get_user(screen_name=username)
    elif handle.api_version == handle.APIVersion.V2:
        return handle.api.get_user(
            username=username, user_fields=fields, user_auth=True
        ).data
    else:
        raise ValueError("Specified version invalid:", handle.api_version)


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
