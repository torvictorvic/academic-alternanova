from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnrollmentViewSet, SubjectViewSet 

router = DefaultRouter()
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'subjects', SubjectViewSet, basename='subject')

urlpatterns = [
    path('', include(router.urls)),
]