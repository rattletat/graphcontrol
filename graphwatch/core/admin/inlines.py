import polymorphic.admin as polyadmin

from graphwatch.twitter.admin import inlines as twitter_inlines

from ..models import Action


class ActionInline(polyadmin.StackedPolymorphicInline):
    model = Action
    child_inlines = twitter_inlines.ACTION_INLINES
    fk_name = "event_monitor"
