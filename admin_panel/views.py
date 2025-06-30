from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from subjects.models import Subject, Enrollment
from users.models import Student, Teacher
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db.models import Avg

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subject(request):
    user = request.user
    if user.role != "admin":
        raise PermissionDenied("Only admins can create subjects.")

    name = request.data.get("name")
    code = request.data.get("code")
    credits = request.data.get("credits")
    teacher_id = request.data.get("teacher_id")

    if not all([name, code, credits, teacher_id]):
        return Response({"error": "Missing required fields."}, status=400)

    try:
        teacher = Teacher.objects.get(user__id=teacher_id)
    except Teacher.DoesNotExist:
        return Response({"error": "Teacher not found."}, status=404)

    subject = Subject.objects.create(
        name=name,
        code=code,
        credits=credits,
        teacher=teacher,
    )

    return Response({"message": "Subject created successfully."})


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def assign_teacher(request, subject_id):
    teacher_id = request.data.get('teacher_id')

    if not teacher_id:
        return Response({"error": "teacher_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return Response({"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        teacher_user = User.objects.get(id=teacher_id)
    except User.DoesNotExist:
        return Response({"error": "Teacher not found."}, status=status.HTTP_404_NOT_FOUND)

    if teacher_user.role != 'teacher':
        return Response({"error": "The user is not a teacher."}, status=status.HTTP_400_BAD_REQUEST)

    subject.teacher = teacher_user.teacher_profile
    subject.save()

    return Response({"message": "Teacher assigned successfully."}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_statistics(request):
    user = request.user

    if user.role != 'admin':
        raise PermissionDenied("Only administrators can access statistics.")

    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_subjects = Subject.objects.count()
    total_enrollments = Enrollment.objects.count()
    average_grade = Enrollment.objects.exclude(grade__isnull=True).aggregate(avg=Avg('grade'))['avg']

    return Response({
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_subjects": total_subjects,
        "total_enrollments": total_enrollments,
        "average_grade": round(average_grade, 2) if average_grade is not None else None
    })