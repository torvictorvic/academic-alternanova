import os
import csv
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, FileResponse, HttpResponseForbidden
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from reportlab.pdfgen import canvas
from django.utils.timezone import now

from subjects.models import Enrollment, Subject
from users.models import Student
from students.models import Enrollment
from .utils import generate_academic_pdf

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_pdf_report(request):
    user = request.user
    role = getattr(user, 'role', None)

    if role not in ['student', 'teacher']:
        return HttpResponseForbidden("Only students or teachers can generate reports.")

    buffer = generate_academic_pdf(user)
    filename = f"{role}_report_{user.id}.pdf"

    return FileResponse(buffer, as_attachment=True, filename=filename)

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_academic_history_csv(request):
    user = request.user

    if user.role != "student":
        raise PermissionDenied("Only students can export their academic history.")

    try:
        student = user.student_profile
    except Student.DoesNotExist:
        return HttpResponse("Student profile not found.", status=404)

    enrollments = Enrollment.objects.filter(student=student).select_related("subject")

    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="academic_history.csv"'

    writer = csv.writer(response)
    writer.writerow(['Subject Name', 'Code', 'Credits', 'Grade', 'Status'])

    for e in enrollments:
        writer.writerow([
            e.subject.name,
            e.subject.code,
            e.subject.credits,
            e.grade if e.grade is not None else '',
            e.status
        ])

    return response