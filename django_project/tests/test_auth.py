"""Регистрация, вход/выход, редиректы и полный сброс пароля."""
import logging
import re
import pytest
from django.test import Client
from django.test.testcases import SimpleTestCase
from django.urls import reverse
from users.models import User
pytestmark=pytest.mark.django_db


def registration():
    return {'username':'newstudent','email':'New@Example.org','phone':'+79991234567','password1':'SecureStudy!2026','password2':'SecureStudy!2026'}


def test_register_logs_in(client,caplog):
    with caplog.at_level(logging.INFO):
        response=client.post(reverse('users:register'),registration())
    user=User.objects.get(username='newstudent')
    SimpleTestCase().assertRedirects(response,reverse('users:profile',args=[user.pk]))
    assert user.email=='new@example.org'
    assert user.check_password('SecureStudy!2026')
    assert int(client.session['_auth_user_id'])==user.pk
    assert 'Регистрация user_id=' in caplog.text
    assert 'SecureStudy!' not in caplog.text

@pytest.mark.parametrize('field,value',[('phone','123'),('email','bad'),('password2','mismatch'),('username','bad name'),('password1','123')])
def test_bad_registration(client,field,value,caplog):
    data=registration();data[field]=value
    response=client.post(reverse('users:register'),data)
    assert response.status_code==200
    assert response.context['form'].errors
    assert not User.objects.exists()
    assert 'Ошибка регистрации' in caplog.text


def test_duplicate_email_case(client,user):
    data=registration();data['email']=user.email.upper()
    response=client.post(reverse('users:register'),data)
    assert 'email' in response.context['form'].errors


def test_login_logout(client,user,caplog):
    with caplog.at_level(logging.INFO):
        response=client.post(reverse('login'),{'username':'learner','password':'Learning!2026'})
        SimpleTestCase().assertRedirects(response,'/')
        assert client.get(reverse('logout')).status_code==405
        response=client.post(reverse('logout'))
        SimpleTestCase().assertRedirects(response,reverse('login'))
    assert '_auth_user_id' not in client.session
    assert 'Успешный вход' in caplog.text and 'Выход user_id=' in caplog.text


def test_bad_login(client,user,caplog):
    response=client.post(reverse('login'),{'username':'learner','password':'wrong-secret'})
    assert response.status_code==200
    assert '_auth_user_id' not in client.session
    assert 'Неудачный вход' in caplog.text
    assert 'wrong-secret' not in caplog.text

@pytest.mark.parametrize('url',['/','/courses/','/schedule/teachers/','/users/','/users/123/','/schedule/students/add/'])
def test_anonymous_redirects(client,url):
    response=client.get(url)
    assert response.status_code==302
    assert response.url.startswith('/auth/login/?next=')


def test_no_external_login_redirect(client,user):
    response=client.post(reverse('login'),{'username':'learner','password':'Learning!2026','next':'https://evil.example/'})
    assert response.url=='/'


def test_password_change(client,user):
    client.force_login(user)
    response=client.post(reverse('password_change'),{'old_password':'Learning!2026','new_password1':'Changed!2027','new_password2':'Changed!2027'})
    assert response.status_code==302
    user.refresh_from_db();assert user.check_password('Changed!2027')
    assert client.get('/').status_code==200


def test_full_file_password_reset(client,user,settings):
    response=client.post(reverse('password_reset'),{'email':user.email})
    SimpleTestCase().assertRedirects(response,reverse('password_reset_done'))
    files=list(settings.EMAIL_FILE_PATH.glob('*'))
    assert len(files)==1
    content=files[0].read_text()
    path=re.search(r'http://testserver(/auth/reset/[^\s]+)',content).group(1)
    response=client.get(path)
    assert response.status_code==302
    confirm=response.url
    assert client.get(confirm).context['validlink']
    response=client.post(confirm,{'new_password1':'Restored!2027','new_password2':'Restored!2027'})
    SimpleTestCase().assertRedirects(response,reverse('password_reset_complete'))
    user.refresh_from_db();assert user.check_password('Restored!2027')
    assert not client.get(path).context['validlink']


def test_csrf_required_for_registration(user):
    client=Client(enforce_csrf_checks=True)
    assert client.post(reverse('users:register'),registration()).status_code==403
