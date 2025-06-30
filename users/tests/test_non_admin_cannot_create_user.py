import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from django.conf import settings

@pytest.mark.django_db
def test_non_admin_cannot_create_user():
    print("USING DATABASE:", settings.DATABASES["default"]["NAME"])

    non_admin_user = baker.make("users.User", role="student", email="student@example.com", username="studentuser")
    refresh = RefreshToken.for_user(non_admin_user)
    token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    payload = {
        "email": "unauthorized@example.com",
        "username": "unauthorized123",
        "first_name": "Unauthorized",
        "last_name": "User",
        "password": "NoAccess123!",
        "role": "teacher"
    }

    response = client.post("/api/admin/create-user/", payload, format="json")

    assert response.status_code == 403
    assert response.data["error"] == "Unauthorized. Only admin can create users."
