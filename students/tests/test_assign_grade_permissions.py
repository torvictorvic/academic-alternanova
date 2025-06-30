import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from django.conf import settings

@pytest.mark.django_db
def test_non_teacher_cannot_assign_grade():
    print("USING DATABASE:", settings.DATABASES["default"]["NAME"])

    # Create a user with the role "student" (it can also be "admin" to test the 403)
    student_user = baker.make("users.User", role="student")
    refresh = RefreshToken.for_user(student_user)
    token = str(refresh.access_token)

    # Create a simulate enrollment
    subject = baker.make("subjects.Subject")
    enrollment = baker.make("students.Enrollment", subject=subject)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    url = f"/api/enrollments/{enrollment.id}/grade/"

    response = client.put(url, {"grade": 4.0}, format="json")

    assert response.status_code == 403
    assert "Only teachers can assign grades." in str(response.data)
