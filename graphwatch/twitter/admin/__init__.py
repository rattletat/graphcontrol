from config import celery_app
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from polymorphic.admin import (
    PolymorphicChildModelAdmin,
    PolymorphicParentModelAdmin,
    PolymorphicChildModelFilter,
)

from django.db.models import Count

from ..models import Account, Handle, Stream, Tweet, actions, events, groups
from ..tasks import update as update_tasks
from .filters import IsBotFilter  # , IsMonitoredFilter
from .forms import ActionForm, GroupForm
from .inlines import HandleInline, TweetInline  # , FollowingInline
from .mixins import ReadOnlyAdmin


@admin.register(Handle)
class HandleAdmin(admin.ModelAdmin):
    list_display = ["account", "api_version", "verified"]
    list_filter = ["api_version", "verified"]
    readonly_fields = ["account", "api_version", "verified"]


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    fields = ["handle", "group", "_get_task_status"]
    readonly_fields = ["_get_task_status"]
    change_form_template = "admin/stream_changeform.html"
    add_form_template = "admin/stream_addform.html"
    # filter_horizontal = ["follow"]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["handle"].queryset = Handle.objects.filter(
            api_version=Handle.APIVersion.V1
        )
        return form

    @admin.display(description="Status")
    def _get_task_status(self, obj):
        task = celery_app.AsyncResult(obj.task_id)
        return task.status

    def response_change(self, request, obj):
        if "_start-stream" in request.POST:
            task = obj._start()
            self.message_user(
                request,
                f"Stream started (Task: {task.task_id} Status: {task.status}",
            )
            return HttpResponseRedirect("..")
        if "_stop-stream" in request.POST:
            task = obj._stop()
            if task:
                self.message_user(
                    request,
                    f"Stream stopped (Task: {task.task_id} Status: {task.status}",
                )
            else:
                self.message_user(request, "No task to stop.")
            return HttpResponseRedirect("..")
        return super().response_change(request, obj)


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
        "view_twitter_profile",
        "twitter_id",
        "description",
        "get_bot_status",
    ]
    readonly_fields = [
        "view_twitter_profile",
        "twitter_id",
        "description",
        "get_bot_status",
    ]
    search_fields = ["username", "name"]
    list_per_page = 10
    save_as_continue = False
    change_form_template = "admin/account_changeform.html"
    add_form_template = "admin/account_addform.html"

    def response_change(self, request, obj):
        if "_fetch-tweets" in request.POST:
            result = update_tasks.update_tweets.delay(obj.twitter_id)
            self.message_user(
                request,
                f"Fetching tweets (Task: {result.task_id} Status: {result.status}",
            )
            return HttpResponseRedirect("..")
        if "_fetch-followers" in request.POST:
            result = update_tasks.update_followers.delay(obj.twitter_id)
            self.message_user(
                request,
                f"Fetching followers (Task: {result.task_id} Status: {result.status}",
            )
            return HttpResponseRedirect("..")
        if "_fetch-following" in request.POST:
            result = update_tasks.update_following.delay(obj.twitter_id)
            self.message_user(
                request,
                f"Fetching following (Task: {result.task_id} Status: {result.status}",
            )
            return HttpResponseRedirect("..")
        return super().response_change(request, obj)

    def get_fields(self, request, account=None):
        if account:  # editing an existing object
            return self.fields
        return ["username"]

    def get_inline_instances(self, request, account=None):
        if not account:
            return []
        inlines = super().get_inline_instances(request, account)
        # if account.monitors.exists():
        #     inlines.insert(0, MonitorInline(self.model, self.admin_site))
        if account.tweets.exists():
            inlines.insert(0, TweetInline(self.model, self.admin_site))
        if hasattr(account, "handle"):
            inlines.insert(0, HandleInline(self.model, self.admin_site))

        return inlines

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            follower_count=Count("followers", distinct=True),
            following_count=Count("following", distinct=True),
            tweet_count=Count("tweets", distinct=True),
        )

    @admin.display(description="Username")
    def view_twitter_profile(self, account):
        return format_html(
            "<a href='https://twitter.com/{username}'>{username}</a>",
            username=account.username,
        )

    @admin.display(description="# Tweets", ordering="-tweet_count")
    def view_tweets_link(self, account):
        count = account.tweet_count
        url = (
            reverse("admin:twitter_tweet_changelist")
            + "?"
            + urlencode({"author": str(account.id)})
        )
        return format_html('<a href="{}">{}</a>', url, count)

    @admin.display(description="# Following", ordering="-following_count")
    def view_following_link(self, account):
        if account.following.exists():
            count = account.following_count
            url = (
                reverse("admin:twitter_account_changelist")
                + "?"
                + urlencode({"followers": str(account.id)})
            )
            return format_html('<a href="{}">{}</a>', url, count)
        else:
            return ""

    @admin.display(description="# Followers", ordering="-follower_count")
    def view_followers_link(self, account):
        if account.followers.exists():
            count = account.follower_count
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
class TweetAdmin(ReadOnlyAdmin):
    search_fields = ["author__username", "author__name", "text"]
    list_display = ["get_author_name", "created_at", "text", "like_count"]
    ordering = ["-created_at"]

    @admin.display(description="Twitter User")
    def get_author_name(self, tweet):
        return tweet.author.name


class TwitterEventChildAdmin(PolymorphicChildModelAdmin):
    """Base admin class for all child models"""

    base_model = events.TwitterEvent

    def has_module_permission(self, request):
        return False


@admin.register(events.TweetEvent)
class TweetEventChildAdmin(TwitterEventChildAdmin):
    base_model = events.TweetEvent


@admin.register(events.FollowEvent)
class FollowEventAdmin(TweetEventChildAdmin):
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
class TwitterEventParentAdmin(PolymorphicParentModelAdmin, ReadOnlyAdmin):

    base_model = events.TwitterEvent
    list_display = ["__str__", "created"]
    ordering = ["-created"]
    polymorphic_list = True
    list_filter = (PolymorphicChildModelFilter,)
    list_per_page = 10
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


@admin.register(actions.FollowAction)
class FollowActionAdmin(LikeActionAdmin):
    base_model = actions.FollowAction


@admin.register(actions.UnfollowAction)
class UnfollowActionAdmin(FollowActionAdmin):
    base_model = actions.UnfollowAction


@admin.register(actions.TweetAction)
class TweetActionAdmin(UnfollowActionAdmin):
    base_model = actions.TweetAction


@admin.register(actions.TwitterAction)
class TwitterActionParentAdmin(PolymorphicParentModelAdmin):

    base_model = actions.TwitterAction
    list_display = ["__str__"]
    list_filter = (PolymorphicChildModelFilter,)
    polymorphic_list = True
    child_models = (
        actions.LikeAction,
        actions.FollowAction,
        actions.UnfollowAction,
        actions.TweetAction,
    )


class TwitterGroupChildAdmin(PolymorphicChildModelAdmin):
    """Base admin class for all child models"""

    base_model = groups.TwitterGroup
    base_form = GroupForm
    filter_horizontal = ["nodes"]

    def has_module_permission(self, request):
        return False


@admin.register(groups.AccountGroup)
class AccountGroupAdmin(TwitterGroupChildAdmin):
    base_model = groups.AccountGroup


@admin.register(groups.TwitterGroup)
class TwitterGroupParentAdmin(PolymorphicParentModelAdmin):

    base_model = groups.AccountGroup
    list_display = ["__str__"]
    list_filter = (PolymorphicChildModelFilter,)
    polymorphic_list = True
    child_models = (groups.AccountGroup,)
