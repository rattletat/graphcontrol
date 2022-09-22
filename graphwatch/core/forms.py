import djhacker
from dal import autocomplete  # , forward
from django import forms

from graphwatch.core.models import Action, Monitor

djhacker.formfield(
    Monitor.source,
    forms.ModelChoiceField,
    widget=autocomplete.ModelSelect2(
        url="monitor_source_autocomplete",
        forward=["event_type"],
        attrs={
            "data-placeholder": "Select source",
        },
    ),
)
djhacker.formfield(
    Monitor.target,
    forms.ModelChoiceField,
    widget=autocomplete.ModelSelect2(
        url="monitor_target_autocomplete",
        forward=["event_type"],
        attrs={
            "data-placeholder": "Select target",
        },
    ),
)
# djhacker.formfield(
#     Action.source,
#     forms.ModelChoiceField,
#     widget=autocomplete.ModelSelect2(
#         url="action_source_autocomplete",
#         forward=["instance"],
#         attrs={
#             "data-placeholder": "Select source",
#         },
#     ),
# )
# djhacker.formfield(
#     Action.target,
#     forms.ModelChoiceField,
#     widget=autocomplete.ModelSelect2(
#         url="action_target_autocomplete",
#         forward=["instance"],
#         attrs={
#             "data-placeholder": "Select target",
#         },
#     ),
# )


class ActionInlineForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if hasattr(self, "instance"):
    #         # self.fields["source"].queryset = self.instance.get_source_queryset()
    #         # self.fields["target"].queryset = self.instance.get_target_queryset()

    class Meta:
        model = Action
        fields = "__all__"
        widgets = {
            "source": autocomplete.ModelSelect2(
                url="action_source_autocomplete",
            ),
            "target": autocomplete.ModelSelect2(
                url="action_target_autocomplete",
            ),
        }
