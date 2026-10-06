"""Кастомный пользователь задан до первой миграции auth."""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from schedule.validators import validate_phone

class User(AbstractUser):
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Телефон', max_length=12, validators=[validate_phone])
    bio = models.TextField('О себе', max_length=1000, blank=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/%Y/%m/', blank=True)
    friends = models.ManyToManyField('self', blank=True, symmetrical=True)
    REQUIRED_FIELDS = ['email', 'phone']
    class Meta:
        constraints = [models.UniqueConstraint(Lower('email'), name='user_email_case_insensitive')]
