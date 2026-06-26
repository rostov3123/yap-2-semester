from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    friends = models.ManyToManyField("self", symmetrical=True, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username
