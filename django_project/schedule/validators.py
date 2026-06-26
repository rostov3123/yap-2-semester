from django.core.exceptions import ValidationError
import re

def validate_phone(value):
    if value and not re.fullmatch(r"\+7\d{10}", value):
        raise ValidationError("Телефон должен быть в формате +79991234567")

def validate_workload(value):
    if value < 0 or value > 60:
        raise ValidationError("Нагрузка должна быть от 0 до 60 часов")

def validate_course_code(value):
    if not re.fullmatch(r"[A-Z]{2,5}-\d{2,4}", value):
        raise ValidationError("Код курса должен выглядеть как PY-101")
