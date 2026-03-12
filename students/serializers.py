from rest_framework import serializers
from django.contrib.auth.models import User
from .models import StudentPerformance, ImportBatch


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


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
