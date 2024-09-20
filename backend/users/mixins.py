import re

from django.core.exceptions import ValidationError


class ValidateUsernameMixin:
    """Миксин для валидации имени пользователя."""

    def validate_username(self, value):
        """Валидация имени пользователя."""
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise ValidationError('Недопустимый никнейм.')
        if value == 'me':
            raise ValidationError('Имя пользователя "me" запрещено.')
        return value


class ValidateEmailMixin:
    """Миксин для валидации email."""

    def validate_email(self, value):
        """Проверка валидности email."""
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", value):
            raise ValidationError("Неверный формат email.")
        return value