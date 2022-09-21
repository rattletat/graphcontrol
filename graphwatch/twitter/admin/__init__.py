from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.urls import path
from django.utils.html import format_html
from django.utils.http import urlencode
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin

from ..models import Account, Handle, Tweet, actions, events
from ..tasks import update as update_tasks
from .filters import IsBotFilter  # , IsMonitoredFilter
from .forms import ActionForm
from .inlines import HandleInline, TweetInline  # , FollowingInline
from .mixins import ReadOnlyAdmin


@admin.register(Handle)
class HandleAdmin(admin.ModelAdmin):
    list_display = ["account", "api_version", "verified"]
    list_filter = ["api_version", "verified"]
    readonly_fields = ["account", "api_version", "verified"]


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "view_tweets_link",
        "view_following_link",
        "view_followers_link",
        "get_bot_status",
    ]
    list_filter = [IsBotFilter]
    fields = [
        "username",
        "twitter_id",
        "description",
        "update_following_button",
        "update_followers_button",
        "update_tweets_button",
        "created",
        "modified",
    ]
    readonly_fields = [
        "twitter_id",
        "description",
        "get_bot_status",
        "update_following_button",
        "update_followers_button",
        "update_tweets_button",
        "created",
        "modified",
    ]
    search_fields = ["username", "name"]
    list_per_page = 10
    save_as_continue = False

    def get_urls(self):
        urls = super().get_urls()
        return urls + [
            path(
                "update-following/<str:account_id>",
                self.update_following,
                name="twitter_update_following",
            ),
            path(
                "update-followers/<str:account_id>",
                self.update_followers,
                name="twitter_update_followers",
            ),
            path(
                "update-tweets/<str:account_id>",
                self.update_tweets,
                name="twitter_update_tweets",
            ),
        ]

    def update_following(self, request, account_id):
        result = update_tasks.update_following.delay(account_id)
        self.message_user(
            request,
            f"Fetching following (Task: {result.task_id} Status: {result.status}",
        )
        return HttpResponseRedirect("../")

    def update_followers(self, request, account_id):
        result = update_tasks.update_followers.delay(account_id)
        self.message_user(
            request,
            f"Fetching followers (Task: {result.task_id} Status: {result.status}",
        )
        return HttpResponseRedirect("../")

    def update_tweets(self, request, account_id):
        result = update_tasks.update_tweets.delay(account_id, count=100)
        self.message_user(
            request, f"Fetching tweets (Task: {result.task_id} Status: {result.status}"
        )
        return HttpResponseRedirect("../")

    def update_following_button(self, account):
        download_view = "admin:twitter_update_following"
        download_url = reverse(download_view, args=[account.twitter_id])
        return format_html('<a href="{}">Update Following</a>', download_url)

    def update_followers_button(self, account):
        download_view = "admin:twitter_update_followers"
        download_url = reverse(download_view, args=[account.twitter_id])
        return format_html('<a href="{}">Update Followers</a>', download_url)

    def update_tweets_button(self, account):
        download_view = "admin:twitter_update_tweets"
        download_url = reverse(download_view, args=[account.twitter_id])
        return format_html('<a href="{}">Update Tweets (Last 100)</a>', download_url)

    def get_readonly_fields(self, request, account=None):
        if account:  # editing an existing object
            return self.readonly_fields + ["username"]
        return self.readonly_fields

    def get_inline_instances(self, request, account=None):
        if not account:
            return []
        inlines = super().get_inline_instances(request, account)
        if hasattr(account, "handle"):
            inlines.insert(0, HandleInline(self.model, self.admin_site))
        # if account.monitors.exists():
        #     inlines.insert(0, MonitorInline(self.model, self.admin_site))
        if account.tweets.exists():
            inlines.insert(0, TweetInline(self.model, self.admin_site))

        return inlines

    @admin.display(description="# Tweets")
    def view_tweets_link(self, account):
        count = Tweet.objects.filter(author=account).count()
        url = (
            reverse("admin:twitter_tweet_changelist")
            + "?"
            + urlencode({"author": str(account.id)})
        )
        return format_html('<a href="{}">{}</a>', url, count)

    @admin.display(description="# Following")
    def view_following_link(self, account):
        if account.following.exists():
            count = account.following.count()
            url = (
                reverse("admin:twitter_account_changelist")
                + "?"
                + urlencode({"followers": str(account.id)})
            )
            return format_html('<a href="{}">{}</a>', url, count)
        else:
            return ""

    @admin.display(description="# Followers")
    def view_followers_link(self, account):
        if account.followers.exists():
            count = account.followers.count()
            url = (
                reverse("admin:twitter_account_changelist")
                + "?"
                + urlencode({"following": str(account.id)})
            )
            return format_html('<a href="{}">{}</a>', url, count)
        else:
            return ""

    @admin.display(description="Is Bot?", boolean=True)
    def get_bot_status(self, account):
        return hasattr(account, "handle") and account.handle.verified

    class Media:
        css = {"all": ["css/admin.css"]}


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    search_fields = ["author__username", "author__name", "text"]
    list_display = ["get_author_name", "created_at", "text", "like_count"]
    ordering = ["-created_at"]

    @admin.display(description="Twitter User")
    def get_author_name(self, tweet):
        return tweet.author.name


class TwitterEventChildAdmin(PolymorphicChildModelAdmin, ReadOnlyAdmin):
    """Base admin class for all child models"""

    base_model = events.TwitterEvent

    def has_module_permission(self, request):
        return False


@admin.register(events.TweetEvent)
class TweetEventAdmin(TwitterEventChildAdmin):
    base_model = events.TweetEvent


@admin.register(events.FollowEvent)
class FollowEventAdmin(TweetEventAdmin):
    base_model = events.FollowEvent


@admin.register(events.UnfollowEvent)
class UnfollowEventAdmin(FollowEventAdmin):
    base_model = events.UnfollowEvent


@admin.register(events.UsernameChangeEvent)
class UsernameChangeEventAdmin(UnfollowEventAdmin):
    base_model = events.UsernameChangeEvent


@admin.register(events.NameChangeEvent)
class NameChangeEventAdmin(UsernameChangeEventAdmin):
    base_model = events.NameChangeEvent


@admin.register(events.DescriptionChangeEvent)
class DescriptionChangeEventAdmin(NameChangeEventAdmin):
    base_model = events.DescriptionChangeEvent


@admin.register(events.TwitterEvent)
class TwitterEventAdmin(PolymorphicParentModelAdmin, ReadOnlyAdmin):

    base_model = events.TwitterEvent
    list_display = ["__str__", "created"]
    ordering = ["-created"]
    polymorphic_list = True
    child_models = (
        events.TweetEvent,
        events.FollowEvent,
        events.UnfollowEvent,
        events.UsernameChangeEvent,
        events.NameChangeEvent,
        events.DescriptionChangeEvent,
    )


class TwitterActionChildAdmin(PolymorphicChildModelAdmin):
    """Base admin class for all child models"""

    base_model = actions.TwitterAction
    base_form = ActionForm

    def has_module_permission(self, request):
        return False


@admin.register(actions.LikeAction)
class LikeActionAdmin(TwitterActionChildAdmin):
    base_model = actions.LikeAction


@admin.register(actions.TwitterAction)
class TwitterActionAdmin(PolymorphicParentModelAdmin):

    base_model = actions.TwitterAction
    list_display = ["__str__"]
    polymorphic_list = True
    child_models = (actions.LikeAction,)
