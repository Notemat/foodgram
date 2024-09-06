from django.forms import ValidationError
from rest_framework import serializers

from recipes.models import Ingridient, Recipe, RecipeIngridient, Tag
from users.serializers import CustomUserSerializer, Base64ImageField


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тэга."""

    class Meta:

        fields = ('id', 'name', 'slug')
        model = Tag


class IngridientSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингридиентов."""

    class Meta:

        fields = ('name', 'measurement_unit')
        model = Ingridient


class RecipeIngridientSerializer(serializers.ModelSerializer):
    """Сериализатор для промежуточной модели рецепта и ингридиента."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingridient.objects.all(),
        source='ingridient',
        required=True,
    )
    name = serializers.CharField(
        required=True,
        source='ingridient.name'
    )
    measurement_unit = serializers.CharField(
        required=True,
        source='ingridient.measurement_unit'
    )

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngridient


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения модели рецепта."""

    author = CustomUserSerializer(many=False, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingridients = RecipeIngridientSerializer(
        many=True,
        read_only=True,
        source='recipe_ingridients'
    )

    class Meta:
        fields = (
            'id', 'tags', 'author',
            'ingridients', 'name', 'image',
            'text', 'cooking_time',
        )
        model = Recipe


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи рецепта."""

    ingridients = RecipeIngridientSerializer(
        many=True,
        required=True,
        source='recipe_ingridients'
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
            'tags', 'image', 'author',
            'ingridients', 'name', 'text',
            'cooking_time'
        )
        model = Recipe

    def create(self, validated_data):
        ingridients_data = validated_data.pop('ingridients')
        recipe = Recipe.objects.create(**validated_data)

        for ingridient_data in ingridients_data:
            RecipeIngridient.objects.create(
                recipe=recipe,
                ingridient=ingridient_data['ingridient'],
                amount=ingridient_data['amount']
            )

        return recipe

    def validate_cooking_time(self, value):
        """Валидация времени приготовления."""

        if value < 1:
            raise ValidationError(
                'Время приготовления не может быть меньше одной минуты'
            )
        return value
