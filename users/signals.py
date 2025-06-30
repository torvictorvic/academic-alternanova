from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Student, Teacher

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.Role.STUDENT:
            Student.objects.create(user=instance)
        elif instance.role == User.Role.TEACHER:
            Teacher.objects.create(user=instance)
