from django import forms
from django.contrib.contenttypes.models import ContentType

from graphwatch.core.models import Node


class TweetInlineForm(forms.BaseInlineFormSet):
    """Base Inline formset to limit inline Model query results."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _kwargs = {self.fk.name: kwargs["instance"]}
        self.queryset = kwargs["queryset"].filter(**_kwargs)[:5]


# class FollowingInlineForm(ModelForm):
#     class Meta:
#         model = Account.following.through
#         fields = ["to_account"]
#         labels = {"to_account": "Account"}


class ActionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        source_ctype = ContentType.objects.get_for_model(self.instance.source_model)
        target_ctype = ContentType.objects.get_for_model(self.instance.target_model)
        self.fields["source"].queryset = Node.objects.filter(
            polymorphic_ctype=source_ctype
        )
        self.fields["target"].queryset = Node.objects.filter(
            polymorphic_ctype=target_ctype
        )


class GroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nodes"].queryset = self.instance.get_nodes_queryset()
