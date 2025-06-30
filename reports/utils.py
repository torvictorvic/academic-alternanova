from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from students.models import Enrollment
from subjects.models import Subject

def generate_academic_pdf(user):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    pdf.setTitle("Academic Report")

    # Header
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "Academic Report")
    y -= 30

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Name: {user.first_name} {user.last_name}")
    y -= 20
    pdf.drawString(50, y, f"Email: {user.email}")
    y -= 30

    if user.role == "student":
        enrollments = Enrollment.objects.filter(student=user)
        if not enrollments.exists():
            pdf.drawString(50, y, "No enrollments found.")
        else:
            pdf.drawString(50, y, "Enrollments:")
            y -= 20
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(50, y, "Subject")
            pdf.drawString(200, y, "Status")
            pdf.drawString(300, y, "Grade")
            pdf.drawString(400, y, "Enrolled At")
            y -= 15
            pdf.setFont("Helvetica", 10)

            grades = []
            for e in enrollments:
                pdf.drawString(50, y, e.subject.name)
                pdf.drawString(200, y, e.status)
                grade = str(e.grade) if e.grade is not None else "-"
                pdf.drawString(300, y, grade)
                pdf.drawString(400, y, e.created_at.strftime("%Y-%m-%d"))
                if e.grade is not None:
                    grades.append(float(e.grade))
                y -= 15

            if grades:
                avg = sum(grades) / len(grades)
                y -= 10
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(50, y, f"General Average: {round(avg, 2)}")

    elif user.role == "teacher":
        
        # subjects = Subject.objects.filter(teacher=user)
        teacher_profile = user.teacher_profile
        subjects = Subject.objects.filter(teacher=teacher_profile)

        if not subjects.exists():
            pdf.drawString(50, y, "No subjects assigned.")
        else:
            pdf.drawString(50, y, "Subjects:")
            y -= 20
            for s in subjects:
                pdf.setFont("Helvetica-Bold", 11)
                pdf.drawString(50, y, f"{s.name}")
                y -= 15
                pdf.setFont("Helvetica", 10)
                enrollments = Enrollment.objects.filter(subject=s)
                if not enrollments.exists():
                    pdf.drawString(70, y, "- No students enrolled.")
                    y -= 15
                else:
                    for e in enrollments:
                        name = f"{e.student.first_name} {e.student.last_name}"
                        status = e.status
                        grade = str(e.grade) if e.grade is not None else "-"
                        pdf.drawString(70, y, f"{name} | Status: {status} | Grade: {grade}")
                        y -= 15

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer
