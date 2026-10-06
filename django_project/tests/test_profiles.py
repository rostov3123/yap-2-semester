"""Приватность профилей, симметричная дружба, аватары и traceback."""
import io
import logging
import pytest
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
pytestmark=pytest.mark.django_db


def test_friend_access_and_removal(client,user,friend,caplog):
    client.force_login(user)
    url=reverse('users:profile',args=[friend.pk])
    assert client.get(url).status_code==403
    with caplog.at_level(logging.INFO):
        assert client.get(reverse('users:add_friend',args=[friend.pk])).status_code==405
        assert not user.friends.exists()
        assert client.post(reverse('users:add_friend',args=[friend.pk])).status_code==302
        assert client.get(url).status_code==200
        assert friend.friends.filter(pk=user.pk).exists()
        client.post(reverse('users:add_friend',args=[friend.pk]))
        assert user.friends.count()==1
        client.post(reverse('users:remove_friend',args=[friend.pk]))
    assert not user.friends.exists() and not friend.friends.exists()
    assert client.get(url).status_code==403
    assert 'Добавление друга' in caplog.text and 'Удаление друга' in caplog.text


def test_cannot_add_self(client,user):
    client.force_login(user)
    assert client.post(reverse('users:add_friend',args=[user.pk])).status_code==403
    assert not user.friends.exists()


def test_edit_own_only(client,user,friend):
    client.force_login(user)
    assert client.post(reverse('users:edit',args=[friend.pk]),{'bio':'hacked'}).status_code==403
    response=client.post(reverse('users:edit',args=[user.pk]),{'first_name':'Иван','last_name':'Соколов','phone':user.phone,'bio':'Изучаю Python','is_superuser':'on'})
    assert response.status_code==302
    user.refresh_from_db();assert user.bio=='Изучаю Python' and not user.is_superuser


def test_invalid_image_logs_traceback(client,user,caplog):
    client.force_login(user)
    upload=SimpleUploadedFile('fake.png',b'not an image',content_type='image/png')
    response=client.post(reverse('users:edit',args=[user.pk]),{'phone':user.phone,'avatar':upload})
    assert response.status_code==200 and 'avatar' in response.context['form'].errors
    assert any(record.exc_info for record in caplog.records if record.name=='users.forms')
    user.refresh_from_db();assert not user.avatar


def test_avatar_private(client,user,friend):
    data=io.BytesIO();Image.new('RGB',(20,20),'green').save(data,format='PNG')
    client.force_login(user)
    response=client.post(reverse('users:edit',args=[user.pk]),{'phone':user.phone,'avatar':SimpleUploadedFile('avatar.png',data.getvalue(),content_type='image/png')})
    assert response.status_code==302
    url=reverse('users:avatar',args=[user.pk])
    response=client.get(url);assert response.status_code==200;response.close()
    client.force_login(friend)
    assert client.get(url).status_code==403
    friend.friends.add(user)
    response=client.get(url);assert response.status_code==200;response.close()
