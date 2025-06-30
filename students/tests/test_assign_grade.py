import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker
from django.conf import settings
from users.models import Teacher, Student

@pytest.mark.django_db
def test_teacher_can_assign_grade():
    print("USING DATABASE:", settings.DATABASES["default"]["NAME"])

    teacher_user = baker.make("users.User", role="teacher")
    teacher, _ = Teacher.objects.get_or_create(user=teacher_user)

    student_user = baker.make("users.User", role="student")
    student, _ = Student.objects.get_or_create(user=student_user)

    subject = baker.make("subjects.Subject", teacher=teacher, is_active=True)
    enrollment = baker.make("subjects.Enrollment", student=student, subject=subject)

    refresh = RefreshToken.for_user(teacher_user)
    token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.put(
        f"/api/enrollments/{enrollment.id}/grade/",
        {"grade": 4.5},
        format="json"
    )

    assert response.status_code == 200
    assert response.data["message"] == "Grade assigned successfully."