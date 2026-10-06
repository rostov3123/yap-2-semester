"""Регистрация и редактирование своего профиля."""
import logging
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
logger = logging.getLogger(__name__)

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','phone','first_name','last_name','password1','password2']
        help_texts = {'phone':'Формат: +79991234567.'}
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Этот email уже зарегистрирован.')
        return email

class LoggedImageField(forms.ImageField):
    """Логировать реальный traceback при отклонении не-изображения."""
    def to_python(self, data):
        try:
            image = super().to_python(data)
            if image and image.size > 2*1024*1024:
                raise forms.ValidationError('Изображение должно быть не больше 2 МБ.')
            return image
        except forms.ValidationError:
            logger.warning('Аватар отклонён: некорректное изображение или размер', exc_info=True)
            raise

class ProfileForm(forms.ModelForm):
    avatar = LoggedImageField(label='Аватар',required=False,help_text='Изображение до 2 МБ.')
    class Meta:
        model = User
        fields = ['first_name','last_name','phone','bio','avatar']
        widgets = {'bio':forms.Textarea(attrs={'rows':4})}
