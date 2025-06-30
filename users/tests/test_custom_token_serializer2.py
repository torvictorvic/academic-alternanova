import pytest
from rest_framework.exceptions import AuthenticationFailed
from users.serializers import CustomTokenObtainPairSerializer
from users.models import User

@pytest.mark.django_db
def test_invalid_login_custom1():
    serializer = CustomTokenObtainPairSerializer(data={"login": "nouser@example.com", "password": "badpass"})
    with pytest.raises(AuthenticationFailed, match="No user found"):
        serializer.is_valid(raise_exception=True)

@pytest.mark.django_db
def test_wrong_password_custom1():
    User.objects.create_user(username="tester1", email="tester1@example.com", password="realpass", role="student")
    serializer = CustomTokenObtainPairSerializer(data={"login": "tester1@example.com", "password": "wrongpass"})
    with pytest.raises(AuthenticationFailed, match="Incorrect password"):
        serializer.is_valid(raise_exception=True)

@pytest.mark.django_db
def test_inactive_user_custom1():
    User.objects.create_user(username="inactive1", email="inactive1@example.com", password="pass123", role="teacher", is_active=False)
    serializer = CustomTokenObtainPairSerializer(data={"login": "inactive1@example.com", "password": "pass123"})
    with pytest.raises(AuthenticationFailed, match="User is inactive"):
        serializer.is_valid(raise_exception=True)

@pytest.mark.django_db
def test_successful_login_custom1():
    User.objects.create_user(username="gooduser1", email="good1@example.com", password="superpass", role="admin")
    serializer = CustomTokenObtainPairSerializer(data={"login": "good1@example.com", "password": "superpass"})
    assert serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    assert "refresh" in data
    assert "access" in data
    assert data["email"] == "good1@example.com"
    assert data["username"] == "gooduser1"
    assert data["role"] == "admin"
