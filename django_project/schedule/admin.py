"""Администрирование учебной системы."""
from django.contrib import admin
from .models import Teacher, TeacherInfo, Course, Student
admin.site.register([Teacher, TeacherInfo, Course, Student])
