from typing import Any, Dict

from django import forms
from django.core.exceptions import ValidationError
from .models import Component


class ComponentForm(forms.ModelForm):
    class Meta:
        model = Component
        fields = "__all__"

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        type_tag = cleaned_data.get("type_tag", None)
        part_only_data = cleaned_data.get("part_only_data", None)
        sub_components = cleaned_data.get("sub_components", None)
        assembly_only_data = cleaned_data.get("assembley_only_data", None)

        if type_tag == Component.TypeTag.Part:
            if sub_components != None:
                raise forms.ValidationError("Part can't have sub_components.")
            elif assembly_only_data != "":
                raise forms.ValidationError(
                    "Part can't have assembly only data.")
        elif type_tag == Component.TypeTag.Assembly:
            if part_only_data != "":
                raise forms.ValidationError(
                    "Assembly can't have part only data.")

        return cleaned_data
