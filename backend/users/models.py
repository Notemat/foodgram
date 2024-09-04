from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(max_length=256, unique=True)
    email = models.EmailField('Электронная почта', max_length=256, unique=True)
    avatar = models.ImageField(
        upload_to='users/avatars/', null=True, default=None
    )
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    """Модель подписки на пользователей."""

    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following'
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'], name='unique_following'
            )
        ]

    def __str__(self) -> str:
        return f'{self.follower} подписан на {self.following}'
