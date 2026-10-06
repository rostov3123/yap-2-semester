"""Все основные страницы и страницы ошибок рендерятся."""
import pytest
from django.urls import reverse
pytestmark=pytest.mark.django_db

@pytest.mark.parametrize('url',['/','/courses/','/courses/1/','/authors/','/authors/1/','/info/','/schedule/teachers/','/schedule/courses/','/schedule/students/','/schedule/orm/','/users/','/auth/password_change/'])
def test_pages(client,user,url):
    client.force_login(user)
    response=client.get(url)
    assert response.status_code==200
    assert '<main' in response.content.decode()

@pytest.mark.parametrize('url',['/courses/999/','/authors/999/','/does-not-exist/'])
def test_404(client,user,settings,url):
    settings.DEBUG=False
    client.force_login(user)
    response=client.get(url)
    assert response.status_code==404
    assert 'Страница не найдена' in response.content.decode()

@pytest.mark.parametrize('url',['/schedule/teachers/add/','/schedule/teachers/add-basic/','/schedule/courses/add/','/schedule/students/add/'])
def test_editor_forms(client,editor,url):
    client.force_login(editor)
    assert client.get(url).status_code==200


def test_seed_idempotent(db):
    from django.core.management import call_command
    from users.models import User
    from schedule.models import Teacher,Course,Student
    call_command('seed_demo');call_command('seed_demo')
    assert User.objects.count()==4
    assert Teacher.objects.count()==3 and Course.objects.count()==3 and Student.objects.count()==3


def test_logging_configuration(settings):
    import logging
    from logging.handlers import RotatingFileHandler,TimedRotatingFileHandler
    handlers=logging.getLogger().handlers
    assert any(isinstance(h,RotatingFileHandler) for h in handlers)
    assert any(isinstance(h,TimedRotatingFileHandler) and h.backupCount==7 for h in handlers)
