import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from django.conf import settings
from users.models import Teacher, Student

@pytest.mark.django_db
def test_teacher_can_list_enrollments():
    print("USING DATABASE:", settings.DATABASES["default"]["NAME"])

    teacher_user = baker.make("users.User", role="teacher")
    teacher, _ = Teacher.objects.get_or_create(user=teacher_user)

    refresh = RefreshToken.for_user(teacher_user)
    token = str(refresh.access_token)

    student_user = baker.make("users.User", role="student")
    student, _ = Student.objects.get_or_create(user=student_user)

    subject = baker.make("subjects.Subject", teacher=teacher, is_active=True)
    baker.make("subjects.Enrollment", student=student, subject=subject)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get("/api/enrollments/")

    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert any(enrollment["subject"] == subject.id for enrollment in response.data)