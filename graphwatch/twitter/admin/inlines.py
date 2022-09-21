from polymorphic.admin import StackedPolymorphicInline

from graphwatch.core.forms import ActionInlineForm

from ..models import actions, nodes
from .forms import TweetInlineForm  # , FollowingInlineForm
from .mixins import ReadOnlyTabularInline


class LikeActionInline(StackedPolymorphicInline.Child):
    model = actions.LikeAction
    form = ActionInlineForm


class FollowActionInline(StackedPolymorphicInline.Child):
    model = actions.FollowAction
    form = ActionInlineForm


class UnfollowActionInline(StackedPolymorphicInline.Child):
    model = actions.UnfollowAction
    form = ActionInlineForm


class TweetActionInline(StackedPolymorphicInline.Child):
    model = actions.TweetAction
    form = ActionInlineForm


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
    fields = ["api_version", "verified"]
    show_change_link = True
    model = nodes.Handle


# class FollowingInline(ReadOnlyTabularInline):
#     # formset = TweetInlineForm
#     fields = ["to_account"]
#     model = Account.following.through
#     fk_name = "from_account"
#     verbose_name_plural = "Following"
#     form = FollowingInlineForm
