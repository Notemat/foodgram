from django.core.exceptions import ValidationError

from djoser.serializers import TokenCreateSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.mixins import ValidateEmailMixin, ValidateUsernameMixin
from users.models import User


class CustomTokenCreateSerializer(TokenObtainPairSerializer):
    """Сериализатор для токена."""

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = User.objects.filter(email=email).first()
        if user is None or not user.check_password(password):
            raise serializers.ValidationError('Неверный email или пароль.')
        attrs['username'] = user.username
        return super().validate(attrs)


class CustomUserSerializer(ValidateUsernameMixin, serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    username = serializers.CharField(max_length=256)

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


# class RegisterDataSerializer(
#     ValidateUsernameMixin, ValidateEmailMixin, serializers.ModelSerializer
# ):
#     """Сериализатор для данных регистрации."""

#     email = serializers.EmailField(max_length=256)
#     username = serializers.CharField(max_length=256)

#     class Meta:
#         model = User
#         fields = ('username', 'email')

#     def validate(self, data):
#         """Проверка уникальности email и username."""
#         email = data.get('email')
#         username = data.get('username')

#         if User.objects.filter(username=username, email=email).exists():
#             return data

#         if User.objects.filter(email=email).exists():
#             raise serializers.ValidationError(
#                 'Этот email уже используется под другим username.'
#             )

#         if User.objects.filter(username=username).exists():
#             raise serializers.ValidationError(
#                 'Имя пользователя используется под другим email.'
#             )

#         return data

    # def create(self, validated_data):
    #     """Создание или получение пользователя."""

    #     user, created = User.objects.get_or_create(
    #         username=validated_data['username'],
    #         email=validated_data['email']
    #     )

    #     return user
