from django.core.exceptions import ValidationError

from djoser.serializers import TokenCreateSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from users.mixins import ValidateEmailMixin, ValidateUsernameMixin
from users.models import User


class EmailTokenObtainSerializer(TokenObtainSerializer):
    """Сериализатор переопределяющий поле username для токена."""
    username_field = User.EMAIL_FIELD

    class Meta:
        model = User


class CustomTokenObtainPairSerializer(EmailTokenObtainSerializer):
    """Сериализатор для получения токена."""

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        return data


class CustomUserSerializer(ValidateUsernameMixin, serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    username = serializers.CharField(max_length=256, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)

    class Meta:
        fields = (
            'email', 'username', 'password', 'first_name', 'last_name'
        )
        extra_kwargs = {
            'is_subscribed': {'read_only': True},
        }
        model = User

    def validate_username(self, value):
        """Валидация имени пользователя."""

        if User.objects.filter(username=value).exists():
            raise ValidationError('Данный username уже используется.')
        return super().validate_username(value)
