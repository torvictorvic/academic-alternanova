import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from django.conf import settings

@pytest.mark.django_db
def test_assign_grade_enrollment_not_found():
    print("USING DATABASE:", settings.DATABASES["default"]["NAME"])

    teacher_user = baker.make("users.User", role="teacher")
    refresh = RefreshToken.for_user(teacher_user)
    token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    invalid_enrollment_id = 9999  # A ID not exists

    response = client.put(f"/api/enrollments/{invalid_enrollment_id}/grade/", {"grade": 4.0}, format="json")

    assert response.status_code == 404
    assert response.data["detail"] == "Enrollment not found."
