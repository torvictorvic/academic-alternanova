from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError

from users.models import Student
from .serializers import EnrollmentSerializer
from users.models import Teacher

from subjects.models import Subject, Enrollment
# from .models import Enrollment

# Create your views here.

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def assign_grade(request, enrollment_id):
    user = request.user

    if user.role != 'teacher':
        raise PermissionDenied("Only teachers can assign grades.")

    try:
        enrollment = Enrollment.objects.select_related('subject').get(id=enrollment_id)
    except Enrollment.DoesNotExist:
        raise NotFound("Enrollment not found.")

    subject = enrollment.subject
    if subject.teacher != user:
        raise PermissionDenied("You are not the teacher of this subject.")

    if not subject.is_active:
        return Response({"error": "Cannot assign grades to an inactive subject."}, status=400)

    grade = request.data.get('grade')
    if grade is None:
        return Response({"error": "Grade is required."}, status=400)

    try:
        enrollment.grade = float(grade)
        enrollment.status = 'completed'
        enrollment.save()
        return Response({"message": "Grade assigned successfully."})
    except ValueError:
        return Response({"error": "Grade must be a valid number."}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_in_subject(request):
    user = request.user

    if user.role != "student":
        raise PermissionDenied("Only students can enroll in subjects.")

    try:
        student = user.student_profile
    except Student.DoesNotExist:
        return Response({"error": "Student profile not found."}, status=404)

    subject_id = request.data.get("subject_id")

    if not subject_id:
        return Response({"error": "Subject ID is required."}, status=400)

    try:
        subject = Subject.objects.get(id=subject_id, is_active=True)
    except Subject.DoesNotExist:
        return Response({"error": "Active subject not found."}, status=404)

    if Enrollment.objects.filter(student=student, subject=subject).exists():
        return Response({"error": "Already enrolled in this subject."}, status=400)

    Enrollment.objects.create(student=student, subject=subject, status="enrolled")

    return Response({"message": "Enrolled successfully."}, status=201)

# View the student grade point average (GPA)
class StudentGPAView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=404)

        completed_enrollments = student.enrollments.filter(status='completed', grade__isnull=False)
        if not completed_enrollments.exists():
            return Response({"gpa": 0.0})

        total_credits = sum(e.subject.credits for e in completed_enrollments)
        if total_credits == 0:
            return Response({"gpa": 0.0})

        weighted_sum = sum(e.grade * e.subject.credits for e in completed_enrollments)
        gpa = round(weighted_sum / total_credits, 2)

        return Response({"gpa": gpa})


# Student academic history
class StudentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        from users.models import User
        students = User.objects.filter(role="student").values("id", "username", "email", "first_name", "last_name")
        return Response(list(students))

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):

        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            raise NotFound("Student not found.")
        '''
        student = Student.objects.get(pk=pk)
        enrollments = student.enrollments.select_related('subject').all()
        '''
        enrollments = student.enrollments.select_related('subject').all()
        data = [
            {
                "subject": enrollment.subject.name,
                "status": enrollment.status,
                "grade": enrollment.grade
            }
            for enrollment in enrollments
        ]
        return Response(data)

