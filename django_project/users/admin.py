"""Управление кастомными пользователями в админке."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
@admin.register(User)
class AcademyUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Профиль', {'fields': ('phone', 'bio', 'avatar', 'friends')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('Контакты', {'fields': ('email', 'phone')}),)
