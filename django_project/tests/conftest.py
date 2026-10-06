"""Фикстуры пользователей, разрешений и учебных сущностей."""
import pytest
from django.contrib.auth.models import Permission
from users.models import User
from schedule.models import Teacher,TeacherInfo,Course,Student

@pytest.fixture(autouse=True)
def isolated_files(settings,tmp_path):
    settings.MEDIA_ROOT=tmp_path/'media'
    settings.EMAIL_FILE_PATH=tmp_path/'mail'
    settings.EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend'

@pytest.fixture
def user(db):
    return User.objects.create_user(username='learner',email='learner@example.org',phone='+79991234567',password='Learning!2026')

@pytest.fixture
def friend(db):
    return User.objects.create_user(username='friend',email='friend@example.org',phone='+79991234568',password='Learning!2026')

@pytest.fixture
def editor(user):
    user.user_permissions.add(*Permission.objects.filter(content_type__app_label='schedule'))
    return user

@pytest.fixture
def teacher(db):
    teacher=Teacher.objects.create(full_name='Анна Волкова',email='teacher@example.org',department='ИТ')
    TeacherInfo.objects.create(teacher=teacher,biography='Биография',office='201')
    return teacher

@pytest.fixture
def course(teacher):
    return Course.objects.create(code='PY-101',title='Основы Python',teacher=teacher,hours=36,capacity=2)

@pytest.fixture
def student(db):
    return Student.objects.create(full_name='Иван Соколов',email='student@example.org',group='ПИ-21')
