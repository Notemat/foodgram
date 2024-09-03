from django import forms

from users.models import User


class UserRegistrationForm(forms.ModelForm):
    """Кастомная форма для регистрации пользовтелей."""

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'first_name', 'last_name')