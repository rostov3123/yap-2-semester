import pytest
from django.urls import reverse
from .models import User

@pytest.fixture
def user(db):
    return User.objects.create_user(username="ada", email="ada@example.com", password="StrongPass123")

@pytest.mark.django_db
def test_register(client):
    response = client.post(reverse("register"), {
        "username": "new_user",
        "email": "new@example.com",
        "phone": "+79991234567",
        "password1": "StrongPass123",
        "password2": "StrongPass123",
    })
    assert response.status_code == 302
    assert User.objects.filter(username="new_user").exists()

@pytest.mark.django_db
def test_login_logout(client, user):
    assert client.login(username="ada", password="StrongPass123")
    response = client.post(reverse("logout"))
    assert response.status_code in {302, 405}

@pytest.mark.parametrize("url_name", ["profile", "user_list"])
@pytest.mark.django_db
def test_auth_required(client, url_name):
    response = client.get(reverse(url_name))
    assert response.status_code == 302
    assert "/auth/login/" in response["Location"]

@pytest.mark.django_db
def test_profile_forbidden_for_not_friend(client, user):
    stranger = User.objects.create_user(username="bob", email="bob@example.com", password="StrongPass123")
    client.login(username="ada", password="StrongPass123")
    response = client.get(reverse("profile_detail", args=[stranger.username]))
    assert response.status_code == 403

@pytest.mark.django_db
def test_bad_registration_errors(client, user):
    response = client.post(reverse("register"), {
        "username": "bad",
        "email": "ada@example.com",
        "password1": "1",
        "password2": "2",
    })
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors
