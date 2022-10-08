from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from polymorphic.admin import StackedPolymorphicInline

from graphwatch.core.forms import ActionInlineForm

from ..models import actions, nodes
from .forms import TweetInlineForm  # , FollowingInlineForm
from .mixins import ReadOnlyTabularInline


class ActionInline(StackedPolymorphicInline.Child):
    form = ActionInlineForm


class LikeActionInline(ActionInline):
    model = actions.LikeAction


class FollowActionInline(ActionInline):
    model = actions.FollowAction


class UnfollowActionInline(ActionInline):
    model = actions.UnfollowAction


class TweetActionInline(ActionInline):
    model = actions.TweetAction


ACTION_INLINES = (
    LikeActionInline,
    FollowActionInline,
    UnfollowActionInline,
    TweetActionInline,
)


class TweetInline(ReadOnlyTabularInline):
    formset = TweetInlineForm
    fields = ["created_at", "text"]
    readonly_fields = ["created_at", "text"]
    model = nodes.Tweet
    fk_name = "author"
    verbose_name = "Last Tweet"
    verbose_name_plural = "Last Tweets"


class HandleInline(ReadOnlyTabularInline):
    fields = ["get_url", "api_version", "verified"]
    readonly_fields = ["get_url"]
    show_change_link = True
    model = nodes.Handle

    @admin.display(description="Link")
    def get_url(self, handle):
        info = (handle._meta.app_label, handle._meta.model_name)
        admin_url = reverse("admin:%s_%s_change" % info, args=(handle.pk,))
        return format_html("<a href='{url}'>Handle</a>", url=admin_url)


# class FollowingInline(ReadOnlyTabularInline):
#     # formset = TweetInlineForm
#     fields = ["to_account"]
#     model = Account.following.through
#     fk_name = "from_account"
#     verbose_name_plural = "Following"
#     form = FollowingInlineForm
