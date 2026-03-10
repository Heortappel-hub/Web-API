from rest_framework import serializers
from .models import StudentPerformance, ImportBatch


class StudentPerformanceSerializer(serializers.ModelSerializer):
    batch_number = serializers.IntegerField(source='batch.batch_number', read_only=True)

    class Meta:
        model = StudentPerformance
        fields = '__all__'


class ImportBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportBatch
        fields = '__all__'


class CSVUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class StudentStatsSerializer(serializers.Serializer):
    total_count = serializers.IntegerField()
    avg_score = serializers.FloatField()
    max_score = serializers.IntegerField()
    min_score = serializers.IntegerField()
    avg_hours_studied = serializers.FloatField()
    avg_attendance = serializers.FloatField()
