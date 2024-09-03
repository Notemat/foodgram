from django.db import models

from users.models import User


# Create your models here.
class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey
    name = models.CharField(max_length=256, verbose_name='Название')
    image = models.ImageField(
        upload_to='reciepes/images/', null=True, default=None
    )
    text = models.TextField(verbose_name='Текстовое описание')
    ingridients = models.ManyToManyField(
        'Ingridient',
        through='RecipeIngridient',
        verbose_name='Ингридиенты'
    )
    tags = models.ManyToManyField(
        'Tag', through='RecipeTag', verbose_name='Тэг'
    )
    cooking_time = models.DurationField(verbose_name='Время приготовления')
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тэга."""

    name = models.CharField(
        max_length=256, unique=True, verbose_name='Название'
    )
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingridient(models.Model):
    """Модель ингридиента."""

    name = models.CharField(max_length=256, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=2, verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


class RecipeIngridient(models.Model):
    """Связанная модель рецепта и ингридиента."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingridient = models.ForeignKey(Ingridient, on_delete=models.CASCADE)
    amount = models.IntegerField()

    def __str__(self) -> str:
        return f'{self.amount} {self.ingridient}'


class RecipeTag(models.Model):
    """Связанная модель рецепта и тага."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.recipe} {self.tags}'


class Favorite(models.Model):
    """Модель избранного."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)