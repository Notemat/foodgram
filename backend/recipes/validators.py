from django.core.exceptions import ValidationError

from recipes.constants import MAX_AMOUNT, MIN_AMOUNT


def amount_validator(amount):
    if not (MIN_AMOUNT <= amount >= MAX_AMOUNT):
        raise ValidationError(
            f"Количество должно быть в пределах от {MIN_AMOUNT} до{MAX_AMOUNT}"
        )
