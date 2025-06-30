import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from django.conf import settings

@pytest.mark.django_db
def test_admin_cannot_create_user_with_duplicate_email():
    print("USING DATABASE:", settings.DATABASES["default"]["NAME"])

    admin_user = baker.make("users.User", role="admin", email="admin@example.com", username="adminuser")
    refresh = RefreshToken.for_user(admin_user)
    token = str(refresh.access_token)

    # Usuario con email duplicado
    baker.make("users.User", email="duplicate@example.com")

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    payload = {
        "email": "duplicate@example.com",
        "username": "anotheruser",
        "first_name": "Dup",
        "last_name": "User",
        "password": "Dup12345!",
        "role": "student"
    }

    response = client.post("/api/admin/create-user/", payload, format="json")

    assert response.status_code == 409
    assert "already exists" in response.data["error"]
