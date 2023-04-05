from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Кастомная модель пользователей."""
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='Почта',
    )
    photo = models.ImageField(
        blank=True,
        null=True,
        upload_to='users/images/',
        verbose_name='Фото'
    )

    class Meta(AbstractUser.Meta):
        ordering = ('username',)
