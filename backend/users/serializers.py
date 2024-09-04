import base64
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model

from djoser.serializers import TokenCreateSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from users.mixins import ValidateEmailMixin, ValidateUsernameMixin
from users.models import User


class Base64ImageField(serializers.ImageField):
    """Сериализатор для декодирования изображений."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split('base64',)
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp' + ext)


class EmailTokenObtainSerializer(TokenObtainPairSerializer):
    """Сериализатор переопределяющий поле username для токена."""

    username_field = User.EMAIL_FIELD


class CustomTokenObtainPairSerializer(EmailTokenObtainSerializer):
    """Сериализатор для получения токена."""

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):

        data = super().validate(attrs)
        print(attrs)
        print('123')

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        return data


class CustomUserSerializer(ValidateUsernameMixin, serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    username = serializers.CharField(max_length=256, required=True)
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = (
            'email', 'username', 'password',
            'first_name', 'last_name', 'avatar'
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


class RegisterDataSerializer(
    ValidateUsernameMixin, ValidateEmailMixin, serializers.ModelSerializer
):
    """Сериализатор для данных регистрации."""

    email = serializers.EmailField(max_length=256)
    username = serializers.CharField(max_length=256)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'first_name', 'last_name',)

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
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name')
        )

        return user
