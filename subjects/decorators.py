from functools import wraps
from rest_framework.exceptions import ValidationError
from subjects.models import Subject


def validate_enrollment(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        data = request.data
        student = request.user.student_profile
        #subject = student.enrollments.model.subject.objects.get(id=data['subject'])
        subject = Subject.objects.get(id=data['subject'])

        # Check credits
        current_credits = sum(
            e.subject.credits for e in student.enrollments.all() if e.status == 'enrolled'
        )
        if current_credits + subject.credits > student.max_credits_per_semester:
            raise ValidationError("Exceeds max credits for the semester.")

        # Check prerequisites
        missing = subject.prerequisites.exclude(
            id__in=student.enrollments.filter(status='completed').values_list('subject_id', flat=True)
        )
        if missing.exists():
            raise ValidationError("Missing prerequisites.")

        return func(self, request, *args, **kwargs)
    return wrapper