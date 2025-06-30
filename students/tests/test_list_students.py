import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from django.conf import settings
from users.models import Student

@pytest.mark.django_db
def test_admin_can_list_students():
    print("USING DATABASE:", settings.DATABASES["default"]["NAME"])

    admin_user = baker.make("users.User", role="admin")
    refresh = RefreshToken.for_user(admin_user)
    token = str(refresh.access_token)

    # Create users with student role
    for _ in range(3):
        baker.make("users.User", role="student")

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = client.get("/api/students/")

    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert len(response.data) >= 3
