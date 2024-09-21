import re
from django.forms import ValidationError
from rest_framework import serializers

from api.mixins import ShoppingCartFavoriteSerializerMixin
from recipes.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Tag
)
from users.serializers import CustomUserSerializer, Base64ImageField


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тэга."""

    class Meta:
        fields = ('id', 'name', 'slug')
        model = Tag

    def validate_slug(self, value):
        """Валидация слага."""
        if not re.match(r'^[-a-zA-Z0-9_]+$', value):
            raise ValidationError('Недопустимый слаг.')
        return value


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингридиентов."""

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для промежуточной модели рецепта и ингридиента."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
        required=True,
    )

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения модели рецепта."""

    author = CustomUserSerializer(many=False, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
        )
        model = Recipe

    def get_ingredients(self, obj):
        """Получаем объекты ингридиента."""
        recipe_ingredients = obj.recipe_ingredients.all()
        return [
            {
                'id': ingredient.ingredient.id,
                'name': ingredient.ingredient.name,
                'measurement_unit': ingredient.ingredient.measurement_unit,
                'amount': ingredient.amount
            }
            for ingredient in recipe_ingredients
        ]

    def get_is_favorited(self, obj):
        """Проверяем, есть ли рецепт в избранном."""
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Проверяем, есть ли рецепт в избранном."""
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи рецепта."""

    ingredients = RecipeIngredientSerializer(
        many=True,
        required=True,
        source='recipe_ingredients'
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True,
        allow_empty=False,
        allow_null=True
    )
    image = Base64ImageField(required=True, allow_null=True)
    name = serializers.CharField(max_length=256, required=True)
    text = serializers.CharField(
        style={'base_template': 'textarea.html'},
        required=True
    )
    cooking_time = serializers.IntegerField(required=True)

    class Meta:
        fields = (
            'tags', 'image',
            'ingredients', 'name', 'text', 'cooking_time'
        )
        model = Recipe

    def validate(self, attrs):
        """Общая валидация полей."""
        request = self.context.get('request')
        if request.method == 'PATCH':
            print(attrs)
            if 'tags' not in attrs:
                raise serializers.ValidationError(
                    'Поле тэгов является обязательным при обновлении.'
                )
        return super().validate(attrs)

    def validate_ingredients(self, ingredients):
        """Валидация ингредиентов."""
        if not ingredients:
            raise serializers.ValidationError(
                'Поле ингредиенты не может быть пустым.'
            )
        unique_ingredients = []
        for ingredient in ingredients:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Ингредиентов не может быть меньше 1.'
                )
            if ingredient['ingredient'] in unique_ingredients:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.'
                )
            unique_ingredients.append(ingredient['ingredient'])
        return ingredients

    def validate_tags(self, tags):
        """Валидация тэгов."""
        if not tags:
            raise serializers.ValidationError(
                'Поле тэги не может быть пустым.'
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Тэги не должны повторяться.'
            )
        return tags

    def validate_cooking_time(self, value):
        """Валидация времени приготовления."""

        if value < 1:
            raise ValidationError(
                'Время приготовления не может быть меньше одной минуты'
            )
        return value

    def add_ingredients_to_recipe(self, recipe, ingredients_data):
        """Добавляем ингредиенты в рецепт."""
        for ingredient_data in ingredients_data:
            ingredient_instance = ingredient_data.get('ingredient')
            if isinstance(ingredient_instance, dict):
                ingredient_instance = ingredient_instance.get('id')
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )

    def create(self, validated_data):
        """Сохраняем ингридиенты и тэги."""
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags_data)
        self.add_ingredients_to_recipe(recipe, ingredients_data)

        return recipe

    def update(self, instance, validated_data):
        """Метод для обновления рецепта."""
        ingredients_data = validated_data.pop('recipe_ingredients', None)
        tags_data = validated_data.pop('tags', None)

        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self.add_ingredients_to_recipe(instance, ingredients_data)
        return instance


class ShoppingCartSerializer(ShoppingCartFavoriteSerializerMixin):
    """Сериализатор для списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('recipe',)

    def create(self, validated_data):
        return self.create_recipe_and_user(ShoppingCart, validated_data)

    def validate(self, data):
        """Валидация подписки на пользователя."""
        return self.validate_recipe_and_user(
            ShoppingCart,
            'Этот рецепт уже в списке покупок.'
        )


class FavoriteSerializer(ShoppingCartFavoriteSerializerMixin):
    """Сериализатор для модели избранного."""

    class Meta:
        model = Favorite
        fields = ('recipe',)

    def create(self, validated_data):
        return self.create_recipe_and_user(Favorite, validated_data)

    def validate(self, data):
        """Валидация подписки на пользователя."""
        return self.validate_recipe_and_user(
            Favorite,
            'Этот рецепт уже в избранном.'
        )
