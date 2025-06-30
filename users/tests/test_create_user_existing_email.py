import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from django.conf import settings
from users.models import User

@pytest.mark.django_db
def test_create_user_with_existing_email():
    print("USING DATABASE:", settings.DATABASES["default"]["NAME"])

    # Crear admin y usuario existente
    admin_user = baker.make("users.User", role="admin")
    existing_user = baker.make("users.User", email="existing@example.com", username="existinguser")

    refresh = RefreshToken.for_user(admin_user)
    token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    payload = {
        "email": "existing@example.com",  # Already exists
        "username": "newusername",
        "first_name": "Test",
        "last_name": "User",
        "password": "Test123!",
        "role": "student"
    }

    response = client.post("/api/admin/create-user/", payload, format="json")

    assert response.status_code == 409
    assert "already exists" in response.data["error"]
