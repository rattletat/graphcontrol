import djhacker
from dal import autocomplete
from django import forms

from graphwatch.core.models import Monitor

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


class ActionInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["source"].queryset = self.instance.get_source_queryset()
        self.fields["target"].queryset = self.instance.get_target_queryset()

    class Meta:
        widgets = {
            "source": autocomplete.ModelSelect2,
            "target": autocomplete.ModelSelect2,
        }
