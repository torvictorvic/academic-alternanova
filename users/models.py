from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)

    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def __str__(self):
        return f"{self.username} ({self.role})"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    max_credits_per_semester = models.PositiveIntegerField(default=18)
    cumulative_average = models.FloatField(default=0.0)

    def __str__(self):
        return f"Student: {self.user.get_full_name()}"
    

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    max_credits_per_semester = models.PositiveIntegerField(default=24)

    def __str__(self):
        return f"Teacher: {self.user.get_full_name()}"