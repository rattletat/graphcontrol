from dal import autocomplete  # , forward
from django import forms

from graphwatch.core.models import Action, Monitor


class MonitorForm(forms.ModelForm):
    class Meta:
        model = Monitor
        fields = "__all__"
        widgets = {
            "source": autocomplete.ModelSelect2(
                url="monitor_source_autocomplete",
                forward=["event_type"],
                attrs={
                    "data-placeholder": "Select source",
                },
            ),
            "target": autocomplete.ModelSelect2(
                url="monitor_target_autocomplete",
                forward=["event_type"],
                attrs={
                    "data-placeholder": "Select target",
                },
            ),
        }


class ActionInlineForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = "__all__"
        widgets = {
            "source": autocomplete.ModelSelect2(
                url="action_source_autocomplete",
                forward=["polymorphic_ctype"],
                attrs={
                    "data-placeholder": "Select source",
                },
            ),
            "target": autocomplete.ModelSelect2(
                url="action_target_autocomplete",
                forward=["polymorphic_ctype"],
                attrs={
                    "data-placeholder": "Select target",
                },
            ),
        }
