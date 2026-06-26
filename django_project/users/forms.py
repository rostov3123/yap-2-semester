import logging
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

logger = logging.getLogger(__name__)

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "phone", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            logger.warning("Registration validation error: duplicate email %s", email)
            raise forms.ValidationError("Такой email уже используется")
        return email

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "phone", "avatar", "bio"]

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar and not avatar.content_type.startswith("image/"):
            logger.exception("Avatar upload is not image: %s", avatar.content_type, exc_info=True)
            raise forms.ValidationError("Загрузите изображение")
        return avatar
