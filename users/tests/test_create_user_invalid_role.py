import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from django.conf import settings

@pytest.mark.django_db
def test_create_user_with_invalid_role():
    print("USING DATABASE:", settings.DATABASES["default"]["NAME"])

    admin_user = baker.make("users.User", role="admin")
    refresh = RefreshToken.for_user(admin_user)
    token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    payload = {
        "email": "not_valid_role@example.com",
        "username": "not_valid_role",
        "first_name": "Bad",
        "last_name": "Role",
        "password": "Invalid123!",
        "role": "hacker"  # not valid role
    }

    response = client.post("/api/admin/create-user/", payload, format="json")

    assert response.status_code == 400
    assert "Invalid role" in response.data["error"]
