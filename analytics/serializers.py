from decimal import Decimal
from django.db.models import Avg
from rest_framework import serializers
from .models import Student, Course, Enrollment, Grade


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = [
            'id', 'enrollment', 'score', 'grade_letter',
            'assignment_name', 'submission_date', 'feedback', 'created_at',
        ]
        read_only_fields = ['grade_letter', 'submission_date', 'created_at']


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    enrollments_count = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email',
            'date_of_birth', 'enrollment_date', 'student_id',
            'is_active', 'created_at', 'updated_at', 'enrollments_count',
        ]
        read_only_fields = ['enrollment_date', 'created_at', 'updated_at']

    def get_enrollments_count(self, obj):
        return obj.enrollments.count()


class CourseSerializer(serializers.ModelSerializer):
    enrollments_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'name', 'code', 'description', 'credits',
            'instructor', 'is_active', 'created_at', 'enrollments_count',
        ]
        read_only_fields = ['created_at']

    def get_enrollments_count(self, obj):
        return obj.enrollments.count()


class EnrollmentSerializer(serializers.ModelSerializer):
    student_detail = StudentSerializer(source='student', read_only=True)
    course_detail = CourseSerializer(source='course', read_only=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), write_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), write_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'course', 'student_detail', 'course_detail',
            'enrollment_date', 'status',
        ]
        read_only_fields = ['enrollment_date']


class EnrollmentPerformanceSerializer(serializers.Serializer):
    """Nested serializer for per-course performance within a student's record."""
    enrollment_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    course_name = serializers.CharField()
    course_code = serializers.CharField()
    status = serializers.CharField()
    average_score = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    grade_count = serializers.IntegerField()


class StudentPerformanceSerializer(serializers.Serializer):
    """Full student info with per-course performance and overall GPA."""
    id = serializers.IntegerField()
    student_id = serializers.CharField()
    full_name = serializers.CharField()
    email = serializers.CharField()
    is_active = serializers.BooleanField()
    overall_gpa = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    enrollments = EnrollmentPerformanceSerializer(many=True)


class CourseStatisticsSerializer(serializers.Serializer):
    """Course info with aggregate statistics."""
    id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField()
    instructor = serializers.CharField()
    credits = serializers.IntegerField()
    student_count = serializers.IntegerField()
    average_score = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    grade_distribution = serializers.DictField(child=serializers.IntegerField())


class TopPerformerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    student_id = serializers.CharField()
    full_name = serializers.CharField()
    email = serializers.CharField()
    gpa = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)


class CoursePerformanceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField()
    instructor = serializers.CharField()
    average_score = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    enrolled_students = serializers.IntegerField()


class AnalyticsSummarySerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    total_courses = serializers.IntegerField()
    total_enrollments = serializers.IntegerField()
    overall_average_score = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
