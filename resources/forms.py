"""Forms for the learning resources app."""

from django import forms

from .models import Resource, ResourceCategory


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = (
            "title",
            "description",
            "link",
            "resource_type",
            "thumbnail",
            "categories",
        )
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
            "link": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "https://..."}
            ),
            "resource_type": forms.Select(attrs={"class": "form-control"}),
            "categories": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user is not None:
            self.fields["categories"].queryset = ResourceCategory.objects.filter(
                user=user
            )
        self.fields["thumbnail"].widget.attrs["class"] = "form-file"

    def save(self, commit=True):
        resource = super().save(commit=False)
        if self.user is not None:
            resource.user = self.user
        if commit:
            resource.save()
            self.save_m2m()
        return resource


class ResourceCategoryForm(forms.ModelForm):
    class Meta:
        model = ResourceCategory
        fields = ("name",)
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Category name"}
            ),
        }
