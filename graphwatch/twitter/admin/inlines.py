from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from polymorphic.admin import StackedPolymorphicInline

from ..models import actions, nodes
from .forms import TweetInlineForm  # , FollowingInlineForm
from .mixins import ReadOnlyTabularInline

# from graphwatch.core.forms import ActionInlineForm


class LikeActionInline(StackedPolymorphicInline.Child):
    model = actions.LikeAction
    # form = ActionInlineForm


class FollowActionInline(StackedPolymorphicInline.Child):
    model = actions.FollowAction
    # form = ActionInlineForm


class UnfollowActionInline(StackedPolymorphicInline.Child):
    model = actions.UnfollowAction
    # form = ActionInlineForm


class TweetActionInline(StackedPolymorphicInline.Child):
    model = actions.TweetAction
    # form = ActionInlineForm


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
