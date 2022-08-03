from django.contrib import admin

from .models import Account, Handle, Tweet


@admin.register(Handle)
class HandleAdmin(admin.ModelAdmin):
    list_display = ["user", "api_version", "verified"]
    readonly_fields = ("user", "api_version", "verified")


class HandleInline(admin.StackedInline):
    fields = [
        "api_key",
        "api_key_secret",
        "access_token",
        "access_token_secret",
        "verified",
        "api_version",
    ]
    readonly_fields = ["verified", "api_version"]
    model = Handle


class IsBotFilter(admin.SimpleListFilter):
    title = "is_bot"
    parameter_name = "is_bot"

    def lookups(self, request, model_admin):
        return (
            ("Yes", "Yes"),
            ("No", "No"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.filter(handle__isnull=True)
        elif value == "No":
            return queryset.exclude(handle__isnull=False)
        return queryset


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["username", "get_bot_status"]
    fields = ["username", "twitter_id", "description"]
    readonly_fields = ("twitter_id", "description")
    save_as_continue = False
    inlines = [HandleInline]

    def get_readonly_fields(self, request, account=None):
        if account:  # editing an existing object
            return self.readonly_fields + ("username",)
        return self.readonly_fields

    @admin.display(description="Is Bot?", boolean=True)
    def get_bot_status(self, account):
        return hasattr(account, "handle") and account.handle.verified


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
