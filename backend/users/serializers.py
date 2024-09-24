import base64

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator

from recipes.serializers import RecipeReadShortSerializer
from users.constants import (
    EMAIL_MAX_LENGTH, NAME_MAX_LENGTH, USERNAME_MAX_LENGTH
)
from users.mixins import ValidateEmailMixin, ValidateUsernameMixin
from users.models import Subscribe, User


class Base64ImageField(serializers.ImageField):
    """Сериализатор для декодирования изображений."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split("base64,")
            ext = format.split("/")[-1].split(";")[0]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
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
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )
        extra_kwargs = {
            "is_subscribed": {"read_only": True},
        }
        model = User

    def get_is_subscribed(self, obj):
        """Проверяем, подписан ли пользователь."""

        user = self.context["request"].user
        if user.is_authenticated:
            return Subscribe.objects.filter(
                user=user, subscription=obj
            ).exists()
        return False

    def validate_username(self, value):
        """Валидация имени пользователя."""

        if User.objects.filter(username=value).exists():
            raise ValidationError("Данный username уже используется.")
        return super().validate_username(value)


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(username=email, password=password)

        if not user:
            raise AuthenticationFailed("Неверные учетные данные")

        attrs["user"] = user
        return attrs


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField(required=True)

    class Meta:
        fields = ("avatar",)
        model = User

    def validate(self, data):
        if "avatar" not in data:
            raise serializers.ValidationError({"avatar": "Обязательное поле"})
        return data


class ChangePasswordSerializer(serializers.ModelSerializer):
    """Сериализатор для смены пароля."""

    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    class Meta:
        fields = ("new_password", "current_password")
        model = User

    def validate(self, data):
        """Проверяем старый и новый пароли."""
        user = self.context["request"].user
        if not user.check_password(data["current_password"]):
            raise serializers.ValidationError(
                {"current_password": "Текущий пароль неверный."}
            )
        validate_password(data["new_password"], user)
        return data


class RegisterDataSerializer(
    ValidateUsernameMixin, ValidateEmailMixin, serializers.ModelSerializer
):
    """Сериализатор для данных регистрации."""

    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Этот email уже используется."
            )
        ],
    )
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Имя пользователя уже занято."
            )
        ],
    )
    first_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH, required=True
    )
    last_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH, required=True
    )

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
        )

    def create(self, validated_data):
        """Создание или получение пользователя."""
        password = validated_data["password"]
        validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        """Скрываем пароль из ответа."""
        representation = super().to_representation(instance)
        representation.pop("password", None)
        return representation


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для записи модели подписок."""

    recipes = RecipeReadShortSerializer(
        many=True, source="subscription.recipes", read_only=True
    )
    subscription = CustomUserSerializer(read_only=True)
    recipes_count = serializers.IntegerField(
        source="subscription.recipes.count", read_only=True
    )

    class Meta:
        fields = ("subscription", "recipes", "recipes_count")
        model = Subscribe

    def validate(self, data):
        """Валидация подписки на пользователя."""
        user = self.context["request"].user
        subscription = self.context["view"].kwargs.get("user_id")
        if user == get_object_or_404(User, id=subscription):
            raise serializers.ValidationError(
                {"errors": "Нельзя подписываться на самого себя."}
            )
        if Subscribe.objects.filter(
            user=user, subscription=get_object_or_404(User, id=subscription)
        ).exists():
            raise serializers.ValidationError(
                {"errors": "Нельзя подписываться на одного человека дважды."}
            )

        return data

    def get_recipes(self, obj):
        """
        Получаем ограниченное количество рецептов подписанных пользователей.
        """
        recipe_limit = self.context.get("recipe_limit")
        recipes_queryset = obj.subscription.recipes.all()
        if recipe_limit:
            recipes_queryset = recipes_queryset[: int(recipe_limit)]

        return RecipeReadShortSerializer(recipes_queryset, many=True).data

    def to_representation(self, instance):
        """Возвращаем в ответе словарь объектов с учетом лимита рецептов."""
        data = super().to_representation(instance)
        request = self.context.get("request")
        recipes_limit = request.query_params.get("recipes_limit")

        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                if recipes_limit < 0:
                    raise ValidationError(
                        "recipes_limit должно быть больше нуля."
                    )
            except ValueError:
                raise ValidationError("recipes_limit должно быть числом.")

            data["recipes"] = data["recipes"][:recipes_limit]

        return {
            **data["subscription"],
            "is_subscribed": True,
            "recipes": data["recipes"],
            "recipes_count": data["recipes_count"],
        }
