from django.forms import ValidationError
from rest_framework import serializers

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from users.serializers import CustomUserSerializer, Base64ImageField


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тэга."""

    class Meta:
        fields = ('id', 'name', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингридиентов."""

    class Meta:
        fields = ('name', 'measurement_unit')
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
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorite', 'name',
            'image', 'text', 'cooking_time',
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

    def get_is_favorite(self, obj):
        """Проверяем, есть ли рецепт в избранном."""
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
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
            'tags', 'image', 'ingredients',
            'name', 'text', 'cooking_time'
        )
        model = Recipe

    def create(self, validated_data):
        """Сохраняем ингридиенты и тэги."""
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
        recipe.tags.set(tags_data)

        return recipe

    def update(self, instance, validated_data):
        """Метод для обновления рецепта."""
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')

        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()

        if tags_data is not None:
            instance.tags.set(tags_data)

        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
        return instance

    def validate_cooking_time(self, value):
        """Валидация времени приготовления."""

        if value < 1:
            raise ValidationError(
                'Время приготовления не может быть меньше одной минуты'
            )
        return value


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    ingredients = serializers.SerializerMethodField()

    class Meta:
        fields = ('ingredients',)
        model = ShoppingCart

    def get_ingredients(self, obj):
        """Получаем ингридиенты для списка."""
        recipies = Recipe.objects.filter(shoppingcart__user=obj.user)
        ingredients = {}

        for recipe in recipies:
            recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe)
            for recipe_ingredient in recipe_ingredients:
                ingredient = recipe_ingredient.ingredient
                if ingredient.name in ingredients:
                    ingredients[ingredient.name]['amount'] += (
                        ingredient.recipeingredient.amount
                    )
                else:
                    ingredients[ingredient.name] = {
                        'amount': recipe_ingredient.amount,
                        'measurement_unit': ingredient.measurement_unit
                    }
        return ingredients


class RecipeReadShortSerializer(serializers.ModelSerializer):
    """Сериализатор для короткого чтения рецепта."""

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели избранного."""

    recipe = RecipeReadShortSerializer(read_only=True)

    class Meta:
        fields = ('recipe',)
        model = Favorite

    def valide(self, attrs):
        """Валидация на дубликат рецепта в избранном."""
        request = self.context['request']
        recipe_id = self.context['view'].kwargs.get('recipe_id')
        if Favorite.objects.filter(
            user=request.user, recipe_id=recipe_id
        ).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже добавлен в избранное.'
            )
        return attrs

    def to_representation(self, instance):
        """Возвращаем в ответе словарь объектов."""
        data = super().to_representation(instance)
        return data['recipe']
