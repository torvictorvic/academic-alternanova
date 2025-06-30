import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from django.conf import settings

@pytest.mark.django_db
def test_teacher_cannot_create_user():
    print("USING DATABASE:", settings.DATABASES["default"]["NAME"])

    teacher_user = baker.make("users.User", role="teacher")
    refresh = RefreshToken.for_user(teacher_user)
    token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    payload = {
        "email": "unauthorized@example.com",
        "username": "unauthuser",
        "first_name": "Test",
        "last_name": "User",
        "password": "NoPass123!",
        "role": "student"
    }

    response = client.post("/api/admin/create-user/", payload, format="json")

    assert response.status_code == 403
    assert "Only admin can create users" in response.data["error"]
