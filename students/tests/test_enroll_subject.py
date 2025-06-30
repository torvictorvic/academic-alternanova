import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from django.conf import settings
from users.models import Student

@pytest.mark.django_db
def test_student_can_enroll_in_subject():
    print("USING DATABASE:", settings.DATABASES["default"]["NAME"])

    student_user = baker.make("users.User", role="student")
    student, _ = Student.objects.get_or_create(user=student_user)

    subject = baker.make("subjects.Subject", is_active=True)

    refresh = RefreshToken.for_user(student_user)
    token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.post(
        "/api/enroll/",
        {"subject_id": subject.id},
        format="json"
    )

    assert response.status_code == 201
    assert "message" in response.data
    assert response.data["message"] == "Enrolled successfully."
