from rest_framework import serializers
from .models import Enrollment,Subject

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["id", "subject", "student", "status", "grade"]
        read_only_fields = ["student", "status", "grade"]

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'credits']

class GradeAssignmentSerializer(serializers.Serializer):
    grade = serializers.FloatField(min_value=0.0, max_value=5.0)