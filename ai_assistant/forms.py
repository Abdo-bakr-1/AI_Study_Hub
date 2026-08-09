"""Forms for the AI chat assistant."""

from django import forms

from .models import Message


class MessageForm(forms.Form):
    """A single chat message submitted by the user."""

    message = forms.CharField(
        max_length=4000,
        widget=forms.Textarea(
            attrs={
                "class": "chat-input",
                "placeholder": "Type your message...",
                "rows": 1,
                "maxlength": 4000,
            }
        ),
    )

    def clean_message(self):
        text = self.cleaned_data["message"].strip()
        if not text:
            raise forms.ValidationError("Please enter a message.")
        return text
