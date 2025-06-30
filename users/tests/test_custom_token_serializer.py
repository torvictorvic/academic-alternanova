import pytest
from rest_framework.exceptions import AuthenticationFailed
from users.serializers import CustomTokenObtainPairSerializer
from users.models import User

@pytest.mark.django_db
def test_invalid_user_login():
    serializer = CustomTokenObtainPairSerializer(data={"login": "nouser@example.com", "password": "fakepass"})
    with pytest.raises(AuthenticationFailed, match="No user found"):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_wrong_password():
    user = User.objects.create_user(username="testuser", email="test@example.com", password="realpass", role="student")
    serializer = CustomTokenObtainPairSerializer(data={"login": "test@example.com", "password": "wrongpass"})
    with pytest.raises(AuthenticationFailed, match="Incorrect password"):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_inactive_user():
    user = User.objects.create_user(username="inactiveuser", email="inactive@example.com", password="pass123", role="teacher", is_active=False)
    serializer = CustomTokenObtainPairSerializer(data={"login": "inactive@example.com", "password": "pass123"})
    with pytest.raises(AuthenticationFailed, match="User is inactive"):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_successful_login():
    user = User.objects.create_user(username="validuser", email="valid@example.com", password="mypassword", role="admin")
    serializer = CustomTokenObtainPairSerializer(data={"login": "valid@example.com", "password": "mypassword"})
    assert serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    assert "refresh" in data
    assert "access" in data
    assert data["email"] == "valid@example.com"
    assert data["username"] == "validuser"
    assert data["role"] == "admin"
