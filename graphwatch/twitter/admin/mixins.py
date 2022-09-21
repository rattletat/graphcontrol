from django.contrib import admin


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False


class ReadOnlyTabularInline(admin.TabularInline):
    extra = 0
    can_delete = False
    editable_fields = []
    readonly_fields = []
    exclude = []

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + [
            field.name
            for field in self.model._meta.fields
            if field.name not in self.editable_fields and field.name not in self.exclude
        ]

    def has_add_permission(self, request, obj=None):
        return False


class FilterQuerySetMixin(admin.StackedInline):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "source":
            kwargs["queryset"] = self.instance.get_source_queryset()
        if db_field.name == "target":
            kwargs["queryset"] = self.instance.get_target_queryset()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
