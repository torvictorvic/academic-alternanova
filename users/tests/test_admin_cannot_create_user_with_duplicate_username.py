import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from django.conf import settings

@pytest.mark.django_db
def test_admin_cannot_create_user_with_duplicate_username():
    print("USING DATABASE:", settings.DATABASES["default"]["NAME"])

    admin_user = baker.make("users.User", role="admin", email="admin@example.com", username="adminuser")
    refresh = RefreshToken.for_user(admin_user)
    token = str(refresh.access_token)

    # Usuario con username duplicado
    baker.make("users.User", username="duplicateuser")

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    payload = {
        "email": "newuser@example.com",
        "username": "duplicateuser",  # duplicate
        "first_name": "Test",
        "last_name": "User",
        "password": "Test1234!",
        "role": "teacher"
    }

    response = client.post("/api/admin/create-user/", payload, format="json")

    assert response.status_code == 409
    assert "Username already taken" in response.data["error"]
