import pytest
from django.urls import reverse
from model_bakery import baker
from users.models import User, Student
from subjects.models import Subject
from rest_framework import status
from core.settings import DATABASES


@pytest.mark.django_db
def test_assign_grade_missing_grade_field(client):
    print("USING DATABASE:", DATABASES["default"]["NAME"])

    # Teacher create a active
    teacher = baker.make("users.Teacher")
    teacher.user.role = "teacher"
    teacher.user.save()

    subject = baker.make(Subject, teacher=teacher, is_active=True)