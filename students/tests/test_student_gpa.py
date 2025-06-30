import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from django.conf import settings
from users.models import Student

@pytest.mark.django_db
def test_student_can_get_gpa():
    print("USING DATABASE:", settings.DATABASES["default"]["NAME"])

    # Create student and user
    student_user = baker.make("users.User", role="student")
    student, _ = Student.objects.get_or_create(user=student_user)

    # Create subjects
    subject1 = baker.make("subjects.Subject", is_active=True)
    subject2 = baker.make("subjects.Subject", is_active=True)

    # Create registrations with grades
    baker.make("subjects.Enrollment", student=student, subject=subject1, grade=4.0)
    baker.make("subjects.Enrollment", student=student, subject=subject2, grade=5.0)

    # JWT
    refresh = RefreshToken.for_user(student_user)
    token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # GET for GPA
    response = client.get(f"/api/students/{student.id}/gpa/")

    assert response.status_code == 200
    assert "gpa" in response.data
    assert float(response.data["gpa"]) == 0.0