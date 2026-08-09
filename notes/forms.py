"""Forms for the notes app."""

from django import forms

from .models import Note, NoteCategory


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ("title", "content", "image", "categories")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(
                attrs={"class": "form-control", "rows": 8}
            ),
            "categories": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user is not None:
            self.fields["categories"].queryset = NoteCategory.objects.filter(
                user=user
            )
        self.fields["image"].widget.attrs["class"] = "form-file"

    def save(self, commit=True):
        note = super().save(commit=False)
        if self.user is not None:
            note.user = self.user
        if commit:
            note.save()
            self.save_m2m()
        return note


class NoteCategoryForm(forms.ModelForm):
    class Meta:
        model = NoteCategory
        fields = ("name",)
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Category name"}
            ),
        }
