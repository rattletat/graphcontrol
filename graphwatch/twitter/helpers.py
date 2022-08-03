import tweepy.errors as tweepy_errors


def determine_API_version(handle):
    try:
        handle.api_version = handle.APIVersion.V2
        get_user_id(handle)
    except tweepy_errors.Forbidden:
        handle.api_version = handle.APIVersion.V1
        get_user_id(handle)


def get_user_tweets(handle, user_id):
    if handle.api_version == handle.APIVersion.V1:
        return handle.api.user_timeline(user_id=user_id, count=10)
    elif handle.api_version == handle.APIVersion.V2:
        return handle.api.get_users_tweets(id=user_id)
    else:
        raise ValueError("Specified version invalid:", handle.api_version)


def get_user_object(handle, username, fields=["description"]):
    if handle.api_version == handle.APIVersion.V1:
        return handle.api.get_user(screen_name=username)
    elif handle.api_version == handle.APIVersion.V2:
        return handle.api.get_user(username=username, user_fields=fields)
    else:
        raise ValueError("Specified version invalid:", handle.api_version)


def get_username(handle):
    if handle.api_version == handle.APIVersion.V1:
        return handle.api.verify_credentials().screen_name
    elif handle.api_version == handle.APIVersion.V2:
        return handle.api.get_me().data.username
    else:
        raise ValueError("Specified version invalid:", handle.api_version)


def get_user_id(handle):
    if handle.api_version == handle.APIVersion.V1:
        return str(handle.api.verify_credentials().id)
    elif handle.api_version == handle.APIVersion.V2:
        return str(handle.api.get_me().data.id)
    else:
        raise ValueError("Specified version invalid:", handle.api_version)


def like_tweet(handle, tweet_id):
    if handle.api_version == handle.APIVersion.V1:
        return handle.api.create_favorite(tweet_id)
    elif handle.api_version == handle.APIVersion.V2:
        return handle.api.like(tweet_id)
    else:
        raise ValueError("Specified version invalid:", handle.api_version)
