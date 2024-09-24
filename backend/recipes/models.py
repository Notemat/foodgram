import random
import string

from django.db import models

from recipes.constants import (
    MAX_LENGTH_INGREDIENT,
    MAX_LENGTH_LINK,
    MAX_LENGTH_NAME,
    MAX_LENGTH_TAGS,
    MAX_LENGTH_UNIT,
)
from users.models import User


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="recipes", verbose_name="Автор"
    )
    name = models.CharField(
        max_length=MAX_LENGTH_NAME, verbose_name="Название"
    )
    image = models.ImageField(
        upload_to="reciepes/images/",
        null=True,
        default=None,
        verbose_name="Изображение",
    )
    text = models.TextField(verbose_name="Текстовое описание")
    ingredients = models.ManyToManyField(
        "Ingredient",
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="Ингридиенты",
    )
    tags = models.ManyToManyField(
        "Tag", through="RecipeTag", verbose_name="Тэг"
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации"
    )
    short_link = models.CharField(
        max_length=MAX_LENGTH_LINK, unique=True,
        blank=True, null=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def save(self, *args, **kwargs):
        if not self.short_link:
            self.short_link = self.generate_short_link()
        super().save(*args, **kwargs)

    def generate_short_link(self):
        """Генерирует уникальную короткую ссылку для рецепта."""
        length = MAX_LENGTH_LINK
        characters = string.ascii_letters + string.digits
        while True:
            short_link = "".join(
                random.choice(characters) for _ in range(length)
            )
            if not Recipe.objects.filter(short_link=short_link).exists():
                return short_link

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тэга."""

    name = models.CharField(
        max_length=MAX_LENGTH_TAGS, unique=True, verbose_name="Название"
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_TAGS, unique=True, verbose_name="Слаг"
    )

    class Meta:
        ordering = ["slug"]
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингридиента."""

    name = models.CharField(
        max_length=MAX_LENGTH_INGREDIENT, verbose_name="Название"
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_UNIT, verbose_name="Единица измерения"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class RecipeIngredient(models.Model):
    """Связанная модель рецепта и ингридиента."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Рецепт"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name="Ингридиент"
    )
    amount = models.PositiveIntegerField(verbose_name="Количество")

    def __str__(self) -> str:
        return (
            f"{self.ingredient} - {self.amount} "
            f"{self.ingredient.measurement_unit}"
        )


class RecipeTag(models.Model):
    """Связанная модель рецепта и тага."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.recipe} {self.tags}"


class ShoppingCartFavoriteBaseModel(models.Model):
    """Базовый класс моделей списка покупок и избранного."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_cart"
            )
        ]


class ShoppingCart(ShoppingCartFavoriteBaseModel):
    """Модель для списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"


class Favorite(ShoppingCartFavoriteBaseModel):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite",
        verbose_name="Пользователь",
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
