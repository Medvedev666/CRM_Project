from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from PIL import Image

from config.settings import MEDIA_URL

class CustomUsernameValidator(RegexValidator):
    def __call__(self, value):
        super().__call__(value)

        # Проверяем, что первые три символа - буквы
        if not value[:1].isalpha():
            raise ValidationError(
                _("Имя пользователя не может начинаться с цифр и символов."),
                code='invalid_username'
            )
        
        if len(value) < 3:
            raise ValidationError(
                _("Имя пользователя слишком короткое."),
                code='invalid_username'
            )

alphanumeric_validator = CustomUsernameValidator(
        regex=r'^[a-zA-Z0-9_-]+$',
        message='Имя пользователя может содержать только английскую раскладку, цифры и символы "-", "_".',
        code='invalid_username'
    )

class CustomUser(AbstractUser):
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        validators=[alphanumeric_validator],
        error_messages={
            'unique': "Пользователь с таким логином уже существует.",
        },
    )
    is_admin = models.BooleanField(default=False)
    address = models.CharField(max_length=60, blank=True, null=True)
    picture = models.ImageField(upload_to='profile_pictures/%y/%m/%d/', default='default.png', null=True)
    month_for_free = models.IntegerField(null=True, blank=True)
    free_ads = models.IntegerField(default=30)
    successful_transactions = models.IntegerField(default=0)
    rating = models.IntegerField(default=0)
    
    objects = UserManager()

    @property
    def get_full_name(self):
        full_name = self.username
        if self.first_name and self.last_name:
            full_name = self.first_name + " " + self.last_name
        return full_name

    def __str__(self):
        return '{} ({})'.format(self.username, self.get_full_name)

    @property
    def get_user_role(self):
        if self.is_superuser or self.is_admin:
            return "Администратор"
        elif not self.is_active:
            return "Вы заблокированы"
        elif self.is_active:
            return "Пользователь"
        else:
            return "Вы не авторизированы"

    def get_picture(self):
        try:
            return self.picture.url
        except:
            no_picture = MEDIA_URL + 'default.png'
            return no_picture

    def get_absolute_url(self):
        return reverse('profile_single', kwargs={'id': self.id})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.picture.path)
            if not self.month and self._state.adding:
                self.month = timezone.now().month
        except:
            pass

    def delete(self, *args, **kwargs):
        if self.picture.url != MEDIA_URL + 'default.png':
            self.picture.delete()
        super().delete(*args, **kwargs)

class Posts(models.Model):
    creater = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    content = models.TextField(blank=True, verbose_name="Текст статьи")
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", verbose_name="Фото")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    is_published = models.BooleanField(default=False, verbose_name="Публикация")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Посты'
        verbose_name_plural = 'Посты'
        ordering = ['-time_create', 'title']
