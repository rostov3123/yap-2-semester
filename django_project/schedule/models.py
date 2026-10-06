"""Преподаватели, профили, курсы и студенты: связи 1:1, 1:N, N:N."""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .validators import validate_person_name, validate_phone, validate_course_code

class Teacher(models.Model):
    full_name = models.CharField('ФИО', max_length=150, validators=[validate_person_name])
    email = models.EmailField('Email', unique=True)
    department = models.CharField('Кафедра', max_length=120, blank=True)
    phone = models.CharField('Телефон', max_length=12, blank=True, validators=[validate_phone])
    experience = models.PositiveIntegerField('Стаж, лет', default=0, validators=[MaxValueValidator(60)])
    class Meta:
        ordering = ['full_name', 'pk']
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
    def __str__(self):
        return self.full_name

class TeacherInfo(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name='info')
    biography = models.TextField('Биография', blank=True)
    office = models.CharField('Кабинет', max_length=30, blank=True)
    def __str__(self):
        return f'Профиль {self.teacher}'

class Course(models.Model):
    code = models.CharField('Код', max_length=10, unique=True, validators=[validate_course_code])
    title = models.CharField('Название', max_length=150)
    description = models.TextField('Описание', blank=True)
    teacher = models.ForeignKey(Teacher, null=True, blank=True, on_delete=models.SET_NULL, related_name='courses', verbose_name='Преподаватель')
    hours = models.PositiveIntegerField('Часы', default=36, validators=[MinValueValidator(1), MaxValueValidator(500)])
    start_date = models.DateField('Начало', null=True, blank=True)
    end_date = models.DateField('Окончание', null=True, blank=True)
    capacity = models.PositiveIntegerField('Мест', default=20, validators=[MinValueValidator(1), MaxValueValidator(200)])
    class Meta:
        ordering = ['title', 'pk']
        constraints = [models.CheckConstraint(condition=models.Q(hours__gte=1, hours__lte=500), name='course_hours_range'),
            models.CheckConstraint(condition=models.Q(capacity__gte=1, capacity__lte=200), name='course_capacity_range'),
            models.CheckConstraint(condition=(models.Q(start_date__isnull=True, end_date__isnull=True) | models.Q(start_date__isnull=False, end_date__isnull=False, end_date__gte=models.F('start_date'))), name='course_date_order')]
    def __str__(self):
        return f'{self.code} · {self.title}'

class Student(models.Model):
    full_name = models.CharField('ФИО', max_length=150, validators=[validate_person_name])
    email = models.EmailField('Email', unique=True)
    group = models.CharField('Группа', max_length=30)
    enrollment_year = models.PositiveIntegerField('Год поступления', default=2026, validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    courses = models.ManyToManyField(Course, blank=True, related_name='students', verbose_name='Курсы')
    class Meta:
        ordering = ['full_name', 'pk']
    def __str__(self):
        return self.full_name
