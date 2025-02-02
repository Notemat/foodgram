# Generated by Django 4.2.15 on 2024-09-28 12:17

from django.db import migrations, models
import recipes.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_alter_favorite_recipe_alter_shoppingcart_recipe_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[recipes.validators.amount_validator], verbose_name='Время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='short_link',
            field=models.CharField(blank=True, max_length=3, null=True, unique=True, verbose_name='Короткая ссылка'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[recipes.validators.amount_validator], verbose_name='Количество'),
        ),
    ]
