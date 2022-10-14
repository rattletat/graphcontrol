import polymorphic.admin as polyadmin
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from graphwatch.core.admin.mixins import ReadOnlyTabularInline
from graphwatch.core.forms import ActionInlineForm

from ..models import actions, nodes
from .forms import GroupsInlineForm, TweetInlineForm


class TwitterActionInline(polyadmin.StackedPolymorphicInline.Child):
    form = ActionInlineForm


class LikeActionInline(TwitterActionInline):
    model = actions.LikeAction


class FollowActionInline(TwitterActionInline):
    model = actions.FollowAction


class UnfollowActionInline(TwitterActionInline):
    model = actions.UnfollowAction


class TweetActionInline(TwitterActionInline):
    model = actions.TweetAction


class RetweetActionInline(TwitterActionInline):
    model = actions.RetweetAction


ACTION_INLINES = (
    LikeActionInline,
    FollowActionInline,
    UnfollowActionInline,
    TweetActionInline,
    RetweetActionInline,
)


class TweetInline(ReadOnlyTabularInline):
    formset = TweetInlineForm
    fields = ["created_at", "text"]
    # readonly_fields = ["created_at", "text"]
    model = nodes.Tweet
    fk_name = "author"
    verbose_name = "Last Tweet"
    verbose_name_plural = "Last Tweets"


class HandleInline(ReadOnlyTabularInline):
    fields = ["get_url", "api_version", "verified"]
    readonly_fields = ["get_url"]
    model = nodes.Handle

    @admin.display(description="Link")
    def get_url(self, handle):
        info = (handle._meta.app_label, handle._meta.model_name)
        admin_url = reverse("admin:%s_%s_change" % info, args=(handle.pk,))
        return format_html("<a href='{url}'>Handle</a>", url=admin_url)


class TwitterGroupInline(ReadOnlyTabularInline):
    fields = ["get_url"]
    readonly_fields = ["get_url"]
    model = nodes.Account.groups.through
    # model = groups.TwitterGroup.nodes.through
    form = GroupsInlineForm
    verbose_name_plural = "Groups"
    max_num = 0

    @admin.display(description="Link")
    def get_url(self, obj):
        group = obj.group.twittergroup
        info = (group._meta.app_label, group._meta.model_name)
        admin_url = reverse("admin:%s_%s_change" % info, args=(group.pk,))
        return format_html("<a href='{url}'>{name}</a>", url=admin_url, name=group.name)


# class FollowingInline(ReadOnlyTabularInline):
#     # formset = TweetInlineForm
#     fields = ["to_account"]
#     model = Account.following.through
#     fk_name = "from_account"
#     verbose_name_plural = "Following"
# form = FollowingInlineForm
