from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from students.models import Enrollment

print("Signal module loaded...")

@receiver(post_save, sender=Enrollment)
def notify_grade_updated(sender, instance, **kwargs):
    if not instance.pk:
        return  # It is not an update, but a creation

    try:
        previous = Enrollment.objects.get(pk=instance.pk)
    except Enrollment.DoesNotExist:
        return

    print(f"Signals => ")
    if previous.grade != instance.grade:
        print(f"Student '{instance.student.user.username}' received a new grade: {instance.grade} for subject '{instance.subject.name}'   [This process should be replaced in the future with an email] ")

