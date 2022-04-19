from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return f'{self.username} - {self.email}'


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name="follower",
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
        blank=True
    )
    author = models.ForeignKey(
        CustomUser,
        related_name="following",
        on_delete=models.CASCADE,
        verbose_name="Автор",
        blank=True
    )

    class Meta:
        verbose_name = 'Подписки пользователя'
        verbose_name_plural = 'Подписки пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name="unique_subscription")]

    def __str__(self) -> str:
        return (f'Пользователь {self.user.username} подписан(а) '
                f'на {self.author.username}')
