import pytest
from model_bakery import baker
from rest_framework.test import APIClient
from users.models import User, Student
from subjects.models import Subject, Enrollment

@pytest.mark.django_db
def test_student_cannot_assign_grade():
    # Crear usuario con rol student
    student_user = User.objects.create_user(username="student_user", password="testpass", role="student")
    client = APIClient()
    client.force_authenticate(user=student_user)

    # Crear un profesor real y una materia activa
    teacher = baker.make("users.Teacher")
    subject = baker.make(Subject, teacher=teacher, is_active=True)

    # Crear el perfil del estudiante (sin violar llave única)
    student_profile, _ = Student.objects.get_or_create(user=student_user)

    # Crear la matrícula
    enrollment = Enrollment.objects.create(student=student_profile, subject=subject, status="enrolled")

    # Intentar asignar nota como estudiante
    url = f"/api/enrollments/{enrollment.id}/grade/"
    response = client.put(url, {"grade": 8.5}, format="json")

    assert response.status_code == 403
    assert "Only teachers can assign grades" in response.data["detail"]
