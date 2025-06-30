from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet
from .views import StudentGPAView
from .views import assign_grade
from students.views import enroll_in_subject

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='students')

urlpatterns = [
    path('', include(router.urls)),
    path('students/<int:student_id>/gpa/', StudentGPAView.as_view(), name='student-gpa'),
    path('enrollments/<int:enrollment_id>/grade/', assign_grade),
    path('enroll/', enroll_in_subject, name='enroll-in-subject'),
]
