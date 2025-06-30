from django.urls import path
from .views import export_academic_history_csv
from .views import generate_pdf_report

urlpatterns = [
    path('history/', export_academic_history_csv, name='export_academic_history'),
    path('pdf/', generate_pdf_report),
]
