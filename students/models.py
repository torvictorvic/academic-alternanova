from django.db import models

# Create your models here.

class Enrollment(models.Model):
    student = models.ForeignKey("users.User", on_delete=models.CASCADE)
    subject = models.ForeignKey("subjects.Subject", on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default="enrolled")
    created_at = models.DateTimeField(auto_now_add=True)