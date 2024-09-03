from django.core.exceptions import ValidationError

from djoser.serializers import TokenCreateSerializer
from rest_framework import serializers

from users.models import User


class CustomTokenCreateSerializer(TokenCreateSerializer):
    """Сериализатор для токена."""

    class Meta:
        fields = ('password', 'email')
        model = User


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    username = serializers.CharField(max_length=256)

    class Meta:
        fields = (
            'email', 'username', 'first_name',
            'last_name', 'avatar', 'is_subscribed'
        )
        model = User

    def validate_username(self, value):
        """Валидация имени пользователя."""

        if User.objects.filter(username=value).exists():
            raise ValidationError('Данный username уже используется.')
        return super().validate_username(value)


class RegisterDataSerializer(
    ValidateUsernameMixin, ValidateEmailMixin, serializers.ModelSerializer
):
    """Сериализатор для данных регистрации."""

    email = serializers.EmailField(max_length=256)
    username = serializers.CharField(max_length=256)

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        """Проверка уникальности email и username."""
        email = data.get('email')
        username = data.get('username')

        if User.objects.filter(username=username, email=email).exists():
            return data

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Этот email уже используется под другим username.'
            )

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                'Имя пользователя используется под другим email.'
            )

        return data

    def create(self, validated_data):
        """Создание или получение пользователя."""

        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            email=validated_data['email']
        )

        return user
