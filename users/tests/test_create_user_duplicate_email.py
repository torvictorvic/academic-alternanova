import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from django.conf import settings
from users.models import User

@pytest.mark.django_db
def test_create_user_with_duplicate_email():
    print("USING DATABASE:", settings.DATABASES["default"]["NAME"])

    existing_user = baker.make("users.User", email="duplicate@example.com", username="existing_user")

    admin_user = baker.make("users.User", role="admin")
    refresh = RefreshToken.for_user(admin_user)
    token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    payload = {
        "email": "duplicate@example.com",  # Already email exists
        "username": "new_username",
        "first_name": "Dup",
        "last_name": "Email",
        "password": "Test123!",
        "role": "student"
    }

    response = client.post("/api/admin/create-user/", payload, format="json")

    assert response.status_code == 409
    assert "email" in response.data["error"]
