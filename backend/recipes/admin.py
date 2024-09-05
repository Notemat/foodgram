from django.contrib import admin
from django.utils.html import format_html

from recipes.forms import AdminTagsRecipeForm
from recipes.models import Ingridient, Recipe, RecipeIngridient, Tag


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн для ингридиентов в админке рецепта"""
    model = RecipeIngridient
    extra = 1
    autocomplete_fields = ('ingridient',)
    verbose_name = 'Ингридиент'
    verbose_name_plural = 'Ингридиенты для рецепта'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    form = AdminTagsRecipeForm
    inlines = (RecipeIngredientInline,)
    readonly_fields = ('image_tag',)
    list_display = (
        'author', 'name', 'image_tag',
        'text',
        'cooking_time', 'pub_date'
    )
    search_fields = ('name',)

    @admin.display(description='Изображение')
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return 'Изображение отсутствует'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Ingridient)
class IngridientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
