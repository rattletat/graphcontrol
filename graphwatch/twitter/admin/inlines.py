from django.forms import BaseInlineFormSet

from ..models import Tweet
from .mixins import ReadOnlyTabularInline


class LastFiveTweetsForm(BaseInlineFormSet):
    """Base Inline formset to limit inline Model query results."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _kwargs = {self.fk.name: kwargs["instance"]}
        self.queryset = kwargs["queryset"].filter(**_kwargs)[:5]


class TweetInline(ReadOnlyTabularInline):
    formset = LastFiveTweetsForm
    fields = ["created_at", "text"]
    readonly_fields = ["created_at", "text"]
    model = Tweet
    fk_name = "user"
    max_num = 5
    verbose_name = "Last Tweet"
    verbose_name_plural = "Last Tweets"
