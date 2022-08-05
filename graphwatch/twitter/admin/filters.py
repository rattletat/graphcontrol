from django.contrib import admin


class IsMonitoredFilter(admin.SimpleListFilter):
    title = "Monitoring"
    parameter_name = "is_monitored"

    def lookups(self, request, model_admin):
        return (
            ("Yes", "Monitored"),
            ("No", "Not Monitored"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.exclude(monitors=None)
        elif value == "No":
            return queryset.filter(monitors=None)
        return queryset


class IsBotFilter(admin.SimpleListFilter):
    title = "Bot Status"
    parameter_name = "is_bot"

    def lookups(self, request, model_admin):
        return (
            ("Yes", "Only Bots"),
            ("No", "Only Humans"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.exclude(handle__isnull=True)
        elif value == "No":
            return queryset.exclude(handle__isnull=False)
        return queryset
