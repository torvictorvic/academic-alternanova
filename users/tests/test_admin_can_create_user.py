import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from django.conf import settings

@pytest.mark.django_db
def test_admin_can_create_user():
    print("USING DATABASE:", settings.DATABASES["default"]["NAME"])

    # Carete admin user
    admin_user = baker.make("users.User", role="admin", email="admin@example.com", username="adminuser")
    refresh = RefreshToken.for_user(admin_user)
    token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    payload = {
        "email": "newuser@example.com",
        "username": "newuser123",
        "first_name": "New",
        "last_name": "User",
        "password": "Secure1234!",
        "role": "student"
    }

    response = client.post("/api/admin/create-user/", payload, format="json")

    assert response.status_code == 201
    assert response.data["email"] == payload["email"]
    assert response.data["username"] == payload["username"]
    assert response.data["role"] == payload["role"]
