from django.urls import path
from .views import create_subject
from .views import assign_teacher
from .views import admin_statistics

urlpatterns = [
    path('subjects/', create_subject),
    path('subjects/<int:subject_id>/assign-teacher/', assign_teacher),
    path('statistics/', admin_statistics),
]
