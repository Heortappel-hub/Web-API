from rest_framework import serializers
from .models import StudentPerformance


class StudentPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPerformance
        fields = '__all__'


class StudentStatsSerializer(serializers.Serializer):
    total_count = serializers.IntegerField()
    avg_score = serializers.FloatField()
    max_score = serializers.IntegerField()
    min_score = serializers.IntegerField()
    avg_hours_studied = serializers.FloatField()
    avg_attendance = serializers.FloatField()
