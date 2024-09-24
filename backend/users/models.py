from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(max_length=USERNAME_MAX_LENGTH, unique=True)
    email = models.EmailField(
        "Электронная почта", max_length=EMAIL_MAX_LENGTH, unique=True
    )
    avatar = models.ImageField(
        upload_to="users/avatars/", null=False, default=None
    )
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        ordering = ["username"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(fields=["email"], name="unique_email"),
            models.UniqueConstraint(
                fields=["username"], name="unique_username"
            ),
        ]


class Subscribe(models.Model):
    """Модель подписки на пользователей."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriptionist"
    )
    subscription = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscribers"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "subscription"], name="unique_following"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} подписан на {self.subscription}"
