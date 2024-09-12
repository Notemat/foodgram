import base64
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db.models import Count

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from recipes.models import Recipe
from recipes.serializers import RecipeReadShortSerializer
from users.constants import (
    EMAIL_MAX_LENGTH, NAME_MAX_LENGTH, USERNAME_MAX_LENGTH
)
from users.mixins import ValidateEmailMixin, ValidateUsernameMixin
from users.models import Subscribe, User


class Base64ImageField(serializers.ImageField):
    """Сериализатор для декодирования изображений."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split('base64,')
            ext = format.split('/')[-1].split(';')[0]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(ValidateUsernameMixin, serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH, required=True
    )
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
            'avatar',
        )
        extra_kwargs = {
            'is_subscribed': {'read_only': True},
        }
        model = User

    def get_is_subscribed(self, obj):
        """Проверяем, подписан ли пользователь."""

        user = self.context['request'].user
        if user.is_authenticated:
            return Subscribe.objects.filter(
                user=user, subscription=obj
            ).exists()

    def validate_username(self, value):
        """Валидация имени пользователя."""

        if User.objects.filter(username=value).exists():
            raise ValidationError('Данный username уже используется.')
        return super().validate_username(value)


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
        refresh = self.get_token(self.user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return data


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = ('avatar',)
        model = User


class ChangePasswordSerializer(serializers.ModelSerializer):
    """Сериализатор для смены пароля."""

    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    class Meta:
        fields = ('new_password', 'current_password')
        model = User

    def validate_password(self, data):
        """Проверяем старый и новый пароли."""
        user = self.context['request'].user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError('Неверный пароль.')
        validate_password(data)
        return data


class RegisterDataSerializer(
    ValidateUsernameMixin, ValidateEmailMixin, serializers.ModelSerializer
):
    """Сериализатор для данных регистрации."""

    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH)
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    first_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH, required=True
    )
    last_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH, required=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'first_name', 'last_name',)

    def create(self, validated_data):
        """Создание или получение пользователя."""

        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name')
        )
        password = validated_data.pop('password')
        if created:
            user.set_password(password)
            user.save()

        return user


class SubscribeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи модели подписок."""

    recipes = RecipeReadShortSerializer(
        many=True, source='subscription.recipes', read_only=True
    )
    subscription = CustomUserSerializer(read_only=True)
    recipes_count = serializers.IntegerField(
        source='subscription.recipes.count', read_only=True
    )

    class Meta:
        fields = ('subscription', 'recipes', 'recipes_count')
        model = Subscribe

    def to_representation(self, instance):
        """Возвращаем в ответе словарь объектов."""
        data = super().to_representation(instance)
        return {
            **data['subscription'],
            'is_subscribed': True,
            'recipes': data['recipes'],
            'recipes_count': data['recipes_count']
        }
