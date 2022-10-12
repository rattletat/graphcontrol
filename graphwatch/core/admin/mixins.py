from django.contrib import admin


class ReadOnlyTabularInline(admin.TabularInline):
    extra = 0
    can_delete = False
    show_change_link = True
    editable_fields = []
    exclude = []

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + [
            field.name
            for field in self.model._meta.fields
            if field.name not in self.editable_fields and field.name not in self.exclude
        ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
