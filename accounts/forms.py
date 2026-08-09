"""Forms for authentication and profile management."""

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)
from django.contrib.auth.models import User

from .models import Profile

BASE_INPUT_CLASS = "form-control"


def _style(fields, css_class=BASE_INPUT_CLASS):
    """Apply a consistent CSS class + placeholder to form widgets."""
    for name, field in fields.items():
        widget = field.widget
        existing = widget.attrs.get("class", "")
        widget.attrs["class"] = (existing + " " + css_class).strip()
        if not widget.attrs.get("placeholder") and field.label:
            widget.attrs["placeholder"] = field.label


class RegisterForm(UserCreationForm):
    """User registration form with an email field."""

    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        # New accounts start inactive until email is verified.
        user.is_active = False
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields)


class UserForm(forms.ModelForm):
    """Edit core user fields (name + email)."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class ProfileForm(forms.ModelForm):
    """Edit extended profile fields including profile picture upload."""

    class Meta:
        model = Profile
        fields = (
            "full_name",
            "bio",
            "profile_picture",
            "date_of_birth",
            "phone",
            "location",
        )
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields)
        # File input keeps its own styling class.
        self.fields["profile_picture"].widget.attrs["class"] = "form-file"

    def clean_profile_picture(self):
        image = self.cleaned_data.get("profile_picture")
        if image and hasattr(image, "size"):
            max_mb = 5
            if image.size > max_mb * 1024 * 1024:
                raise forms.ValidationError(
                    f"Image file too large (max {max_mb} MB)."
                )
        return image


class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields)


class PasswordResetRequestForm(forms.Form):
    """Ask for the email address to send a reset link to."""

    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields)


class SetNewPasswordForm(forms.Form):
    """Collect and validate a new password during reset."""

    new_password1 = forms.CharField(
        label="New password", widget=forms.PasswordInput
    )
    new_password2 = forms.CharField(
        label="Confirm new password", widget=forms.PasswordInput
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields)

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("new_password1")
        p2 = cleaned.get("new_password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("The two password fields did not match.")
        if p1 and len(p1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        return cleaned
