from django.contrib import admin
from django.shortcuts import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from ..models import Account, Handle, Tweet
from .filters import IsBotFilter, IsMonitoredFilter
from .inlines import HandleInline, TweetInline


@admin.register(Handle)
class HandleAdmin(admin.ModelAdmin):
    list_display = ["user", "api_version", "verified"]
    list_filter = ["api_version", "verified"]
    readonly_fields = ("user", "api_version", "verified")


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["name", "view_tweets_link", "get_bot_status"]
    list_filter = [IsBotFilter, IsMonitoredFilter]
    fields = ["username", "twitter_id", "description"]
    readonly_fields = ["twitter_id", "description", "get_bot_status"]
    save_as_continue = False
    inlines = [TweetInline]

    def get_readonly_fields(self, request, account=None):
        if account:  # editing an existing object
            return self.readonly_fields + ["username"]
        return self.readonly_fields

    def get_inline_instances(self, request, account=None):
        if not account:
            return []
        inlines = super().get_inline_instances(request, account)
        if hasattr(account, "handle"):
            inlines.append(HandleInline(self.model, self.admin_site))
        return inlines

    @admin.display(description="# Tweets")
    def view_tweets_link(self, account):
        count = Tweet.objects.filter(user=account).count()
        url = (
            reverse("admin:twitter_tweet_changelist")
            + "?"
            + urlencode({"user": str(account.id)})
        )
        return format_html('<a href="{}">{}</a>', url, count)

    @admin.display(description="Is Bot?", boolean=True)
    def get_bot_status(self, account):
        return hasattr(account, "handle") and account.handle.verified


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "text"]
    # list_filter = ["user"]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
