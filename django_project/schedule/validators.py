"""Переиспользуемые валидаторы полей учебной системы."""
import re
from django.core.exceptions import ValidationError


def validate_person_name(value):
    """Разрешить ФИО из букв с пробелами, дефисами и апострофами."""
    if len(value.strip().split()) < 2 or not all(c.isalpha() or c in " -'" for c in value):
        raise ValidationError('Укажите минимум имя и фамилию, без цифр.', code='invalid_name')


def validate_phone(value):
    """Проверить нормализованный российский телефон."""
    if not re.fullmatch(r'\+7[0-9]{10}', value):
        raise ValidationError('Формат телефона: +79991234567.', code='invalid_phone')


def validate_course_code(value):
    """Код курса: 2–6 заглавных латинских букв, дефис, три цифры."""
    if not re.fullmatch(r'[A-Z]{2,6}-[0-9]{3}', value):
        raise ValidationError('Пример кода курса: PY-101.', code='invalid_code')
