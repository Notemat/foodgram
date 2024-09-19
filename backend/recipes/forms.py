from django import forms

from recipes.models import Recipe, Tag


class MinutesInput(forms.TextInput):
    """Виджет для ввода времени в минутах."""

    def init(self, attrs=None):
        default_attrs = {'placeholder': 'Введите количество минут'}
        if attrs:
            default_attrs.update(attrs)
        super().init(attrs=default_attrs)


class AdminTagsRecipeForm(forms.ModelForm):
    """Форма для отображение тэгов в модели рецепта."""

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=True,
        label='Тэг'
    )
    cooking_time = forms.IntegerField(
        widget=MinutesInput(),
        help_text='Введите количество минут',
        label='Время приготовления'
    )

    class Meta:
        model = Recipe
        fields = ('name', 'tags', 'cooking_time', 'text', 'image', 'author',)
