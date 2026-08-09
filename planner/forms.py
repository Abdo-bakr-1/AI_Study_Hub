"""Forms for the study planner (tasks)."""

from django import forms

from .models import Task, TaskCategory


class TaskForm(forms.ModelForm):
    """Create / edit a task. Categories are limited to the current user."""

    class Meta:
        model = Task
        fields = (
            "title",
            "description",
            "due_date",
            "priority",
            "status",
            "categories",
        )
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
            "due_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "priority": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "categories": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user is not None:
            self.fields["categories"].queryset = TaskCategory.objects.filter(
                user=user
            )

    def save(self, commit=True):
        task = super().save(commit=False)
        # Keep is_completed and status in sync.
        task.is_completed = task.status == Task.Status.COMPLETED
        if self.user is not None:
            task.user = self.user
        if commit:
            task.save()
            self.save_m2m()
        return task


class TaskCategoryForm(forms.ModelForm):
    class Meta:
        model = TaskCategory
        fields = ("name",)
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Category name"}
            ),
        }
