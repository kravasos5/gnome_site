from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.text import slugify
import random, string

class AdvUser(AbstractUser):
    def get_profile_image_path(self, filename):
        username = self.username
        return f'photos/{username}/{filename}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.username}')#-{"".join(random.choices(string.ascii_lowercase, k=10))}')[:200]
        super().save(*args, **kwargs)

    is_activated = models.BooleanField(default=True, db_index=True,
                                       verbose_name='Прошёл активацию?')
    send_messages = models.BooleanField(default=True,
                        verbose_name='Слать оповещения о комментариях?')
    avatar = models.ImageField(verbose_name='Аватар',
                              upload_to=get_profile_image_path,
                              null=True, db_index=True)
    profile_image = models.ImageField(verbose_name='Шапка профиля',
                              upload_to=get_profile_image_path,
                              null=True, db_index=True)
    status = models.CharField(max_length=50, null=True, blank=True,
                              db_index=True, verbose_name='Статус профиля')
    description = models.CharField(max_length=500, null=True, blank=True,
                              db_index=True, verbose_name='Описание профиля')
    subscriptions = models.ManyToManyField('self', blank=True, symmetrical=False, verbose_name='Подписчики')
    slug = models.SlugField(max_length=200, unique=True, db_index=True,
                            verbose_name='Слаг')

    class Meta(AbstractUser.Meta):
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'<{self.username}>'

    def get_absolute_url(self):
        return reverse('gnome_main:user-profile', kwargs={'slug': self.slug})