from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from .models import Subject
from .serializers import SubjectSerializer

from .models import Enrollment
from .serializers import EnrollmentSerializer, GradeAssignmentSerializer
from .decorators import validate_enrollment
from users.models import Student 
from users.models import Teacher
# from users.serializers import StudentSerializer


# Create your views here.
class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["get"], url_path="students")
    def list_students(self, request, pk=None):
        user = request.user

        # Check teacher
        if request.user.role != "teacher":
            raise PermissionDenied("Only teachers can access this information.")

        subject = self.get_object()
        enrollments = Enrollment.objects.filter(subject=subject).select_related("student", "student__user")

        data = []
        for enrollment in enrollments:
            student = enrollment.student.user
            student_name = f"{student.first_name or ''} {student.last_name or ''}".strip()
            if not student_name:
                student_name = student.username

            data.append({
                "student_name": student_name,
                "student_id": enrollment.student.id,
                "status": enrollment.status,
                "grade": enrollment.grade,
            })

        return Response(data)
    
    @action(detail=False, methods=["get"], url_path="me")
    def my_subjects(self, request):
        user = request.user
        if user.role != "teacher":
            raise PermissionDenied("Only teachers can access this information.")

        try:
            teacher = user.teacher_profile
        except Teacher.DoesNotExist:
            return Response({"detail": "Teacher profile not found."}, status=status.HTTP_404_NOT_FOUND)

        subjects = Subject.objects.filter(teacher=teacher)
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="students")
    def list_students(self, request, pk=None):
        user = request.user

        # Check teacher
        if user.role != "teacher":
            raise PermissionDenied("Only teachers can access this information.")

        subject = self.get_object()

        # Check subject - teacher profile
        if subject.teacher != user.teacher_profile:
            raise PermissionDenied("You can only view students from your own subjects.")

        enrollments = Enrollment.objects.filter(subject=subject).select_related("student__user")

        data = []
        for enrollment in enrollments:
            student_user = enrollment.student.user
            data.append({
                "student_id": enrollment.student.id,
                "student_name": f"{student_user.first_name} {student_user.last_name}".strip(),
                "email": student_user.email,
                "status": enrollment.status,
                "grade": enrollment.grade,
            })

        return Response(data)

    # Complete subject
    @action(detail=True, methods=["put"], url_path="complete")
    def complete_subject(self, request, pk=None):
        user = request.user

        if user.role != "teacher":
            raise PermissionDenied("Only teachers can perform this action.")

        subject = self.get_object()

        if subject.teacher != user.teacher_profile:
            raise PermissionDenied("You can only complete your own subjects.")

        enrollments = Enrollment.objects.filter(subject=subject)

        if enrollments.filter(grade__isnull=True).exists():
            raise ValidationError("All students must be graded before completing the subject.")

        subject.is_active = False
        subject.save()

        return Response({"message": "Subject completed successfully."})

    # Re-Open subject
    @action(detail=True, methods=["put"], url_path="reopen")
    def reopen_subject(self, request, pk=None):
        user = request.user

        if user.role != "teacher":
            raise PermissionDenied("Only teachers can perform this action.")

        subject = self.get_object()

        if subject.teacher != user.teacher_profile:
            raise PermissionDenied("You can only reopen your own subjects.")

        if subject.is_active:
            return Response({"message": "Subject is already active."}, status=status.HTTP_400_BAD_REQUEST)

        subject.is_active = True
        subject.save()

        return Response({"message": "Subject reopened successfully."})

    # List completed subjects
    @action(detail=False, methods=["get"], url_path="completed")
    def completed_subjects(self, request):
        user = request.user

        if user.role != "teacher":
            raise PermissionDenied("Only teachers can access this information.")

        try:
            teacher = user.teacher_profile
        except Teacher.DoesNotExist:
            return Response({"detail": "Teacher profile not found."}, status=status.HTTP_404_NOT_FOUND)

        subjects = Subject.objects.filter(teacher=teacher, is_active=False)
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

    # List active subjects with teacher 
    @action(detail=False, methods=["get"], url_path="active")
    def active_subjects(self, request):
        user = request.user

        if user.role != "teacher":
            raise PermissionDenied("Only teachers can access this information.")

        try:
            teacher = user.teacher_profile
        except Teacher.DoesNotExist:
            return Response({"detail": "Teacher profile not found."}, status=status.HTTP_404_NOT_FOUND)

        subjects = Subject.objects.filter(teacher=teacher, is_active=True)
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

# Enrollment and grading views
class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]


    # @validate_enrollment
    def create(self, request, *args, **kwargs):
        user = request.user
        if user.role != "student":
            raise PermissionDenied("Only students can enroll in subjects.")

        subject_id = request.data.get("subject")
        if not subject_id:
            raise ValidationError({"subject": "This field is required."})

        try:
            student = user.student_profile
        except AttributeError:
            raise ValidationError("Student profile not found.")

        # Validate if you are already registered
        if Enrollment.objects.filter(student=student, subject_id=subject_id).exists():
            raise ValidationError("You are already enrolled in this subject.")

        subject = Subject.objects.get(id=subject_id)

        # Validate prerequisites
        missing_prereqs = subject.prerequisites.exclude(
            id__in=Enrollment.objects.filter(
                student=student, status="completed"
            ).values_list("subject_id", flat=True)
        )
        if missing_prereqs.exists():
            missing_names = [s.name for s in missing_prereqs]
            raise ValidationError(f"Missing prerequisites: {', '.join(missing_names)}")

        # Validate credit limit
        total_credits = sum(
            e.subject.credits
            for e in Enrollment.objects.filter(student=student)
        ) + subject.credits

        if total_credits > student.max_credits_per_semester:
            raise ValidationError("You are exceeding your credit limit for this semester.")

        # Save enrollment manually by assigning student
        serializer = self.get_serializer(data={"subject": subject_id})
        serializer.is_valid(raise_exception=True)
        serializer.save(student=student)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
    @action(detail=False, methods=["get"], url_path="me/subjects")
    def my_subjects(self, request):
        user = request.user

        # Check student
        if user.role != "student":
            raise PermissionDenied("Only students can access this information.")

        # Read student profile
        try:
            student = user.student_profile
        except Student.DoesNotExist:
            return Response({"detail": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Read inscriptions
        enrollments = Enrollment.objects.filter(student=student).select_related("subject")

        data = [
            {
                "subject_id": enrollment.subject.id,
                "subject_name": enrollment.subject.name,
                "grade": enrollment.grade,
                "status": enrollment.status,
            }
            for enrollment in enrollments
        ]

        return Response(data)


    # Teachers can grade. 
    @action(detail=True, methods=["put"], url_path="grade")
    def assign_grade(self, request, pk=None):
        user = request.user
        if user.role != "teacher":
            raise PermissionDenied("Only teachers can assign grades.")

        try:
            enrollment = Enrollment.objects.select_related("subject").get(pk=pk)
        except Enrollment.DoesNotExist:
            return Response({"detail": "Enrollment not found."}, status=status.HTTP_404_NOT_FOUND)

        if enrollment.subject.teacher != user.teacher_profile:
            raise PermissionDenied("You can only grade students in your own subjects.")

        serializer = GradeAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        grade = serializer.validated_data["grade"]
        enrollment.grade = grade
        enrollment.status = "completed"
        enrollment.save()

        return Response({"message": "Grade assigned successfully."})
    

    # Student see subjects grades
    @action(detail=False, methods=["get"], url_path="me/subjects/grades")
    def subjects_by_grade(self, request):
        user = request.user
        if user.role != "student":
            raise PermissionDenied("Only students can access this information.")

        try:
            student = user.student_profile
        except Student.DoesNotExist:
            return Response({"detail": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)

        enrollments = Enrollment.objects.filter(student=student, status="completed").select_related("subject")

        approved = []
        failed = []

        for enrollment in enrollments:
            subject_info = {
                "subject_id": enrollment.subject.id,
                "subject_name": enrollment.subject.name,
                "grade": enrollment.grade,
            }

            if enrollment.grade >= 3.0:
                approved.append(subject_info)
            else:
                failed.append(subject_info)

        return Response({
            "approved": approved,
            "failed": failed
        })
    

    # Student averages
    @action(detail=False, methods=["get"], url_path="me/average")
    def average_grade(self, request):
        user = request.user

        if user.role != "student":
            raise PermissionDenied("Only students can access this information.")

        try:
            student = user.student_profile
        except Student.DoesNotExist:
            return Response({"detail": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)

        completed_enrollments = Enrollment.objects.filter(student=student, status="completed", grade__isnull=False)

        if not completed_enrollments.exists():
            return Response({"average": None, "detail": "No completed subjects found."})

        average = sum(e.grade for e in completed_enrollments) / completed_enrollments.count()

        return Response({"average": round(average, 2)})


    # Student history
    @action(detail=False, methods=["get"], url_path="me/history")
    def academic_history(self, request):
        user = request.user

        if user.role != "student":
            raise PermissionDenied("Only students can access this information.")

        try:
            student = user.student_profile
        except Student.DoesNotExist:
            return Response({"detail": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)

        enrollments = Enrollment.objects.filter(student=student).select_related("subject")

        data = [
            {
                "subject_id": enrollment.subject.id,
                "subject_name": enrollment.subject.name,
                "grade": enrollment.grade,
                "status": enrollment.status,
            }
            for enrollment in enrollments
        ]

        return Response(data)