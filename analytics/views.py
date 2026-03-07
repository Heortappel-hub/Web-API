from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Avg, Count, Q
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django_filters.rest_framework import DjangoFilterBackend

from .models import Student, Course, Enrollment, Grade
from .serializers import (
    StudentSerializer,
    CourseSerializer,
    EnrollmentSerializer,
    GradeSerializer,
    StudentPerformanceSerializer,
    CourseStatisticsSerializer,
    TopPerformerSerializer,
    CoursePerformanceSerializer,
    AnalyticsSummarySerializer,
)


def _round(value):
    """Round a Decimal to 2 decimal places."""
    if value is None:
        return None
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'student_id']
    ordering_fields = ['enrollment_date', 'last_name']
    ordering = ['last_name']

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        student = self.get_object()
        enrollments = student.enrollments.select_related('course').prefetch_related('grades')

        enrollment_data = []
        all_scores = []

        for enrollment in enrollments:
            grades = enrollment.grades.all()
            scores = [float(g.score) for g in grades]
            avg_score = _round(sum(scores) / len(scores)) if scores else None
            if avg_score is not None:
                all_scores.append(float(avg_score))

            enrollment_data.append({
                'enrollment_id': enrollment.id,
                'course_id': enrollment.course.id,
                'course_name': enrollment.course.name,
                'course_code': enrollment.course.code,
                'status': enrollment.status,
                'average_score': avg_score,
                'grade_count': len(scores),
            })

        overall_gpa = _round(sum(all_scores) / len(all_scores)) if all_scores else None

        data = {
            'id': student.id,
            'student_id': student.student_id,
            'full_name': student.full_name,
            'email': student.email,
            'is_active': student.is_active,
            'overall_gpa': overall_gpa,
            'enrollments': enrollment_data,
        }

        serializer = StudentPerformanceSerializer(data)
        return Response(serializer.data)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'instructor']
    ordering_fields = ['name', 'code']
    ordering = ['code']

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        course = self.get_object()
        enrollments = course.enrollments.prefetch_related('grades')

        student_count = enrollments.count()
        all_scores = []
        grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}

        for enrollment in enrollments:
            for grade in enrollment.grades.all():
                all_scores.append(float(grade.score))
                letter = grade.grade_letter
                if letter in grade_distribution:
                    grade_distribution[letter] += 1

        average_score = _round(sum(all_scores) / len(all_scores)) if all_scores else None

        data = {
            'id': course.id,
            'name': course.name,
            'code': course.code,
            'instructor': course.instructor,
            'credits': course.credits,
            'student_count': student_count,
            'average_score': average_score,
            'grade_distribution': grade_distribution,
        }

        serializer = CourseStatisticsSerializer(data)
        return Response(serializer.data)


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related('student', 'course')
    serializer_class = EnrollmentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'course', 'status']
    ordering_fields = ['enrollment_date']
    ordering = ['-enrollment_date']


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.select_related('enrollment')
    serializer_class = GradeSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['enrollment']
    ordering_fields = ['submission_date', 'score']
    ordering = ['-submission_date']


class AnalyticsViewSet(ViewSet):

    @action(detail=False, methods=['get'])
    def summary(self, request):
        total_students = Student.objects.count()
        total_courses = Course.objects.count()
        total_enrollments = Enrollment.objects.count()

        avg_result = Grade.objects.aggregate(avg=Avg('score'))
        overall_average_score = _round(avg_result['avg'])

        data = {
            'total_students': total_students,
            'total_courses': total_courses,
            'total_enrollments': total_enrollments,
            'overall_average_score': overall_average_score,
        }

        serializer = AnalyticsSummarySerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='top-performers')
    def top_performers(self, request):
        students = Student.objects.prefetch_related('enrollments__grades')
        performers = []

        for student in students:
            all_scores = []
            for enrollment in student.enrollments.all():
                for grade in enrollment.grades.all():
                    all_scores.append(float(grade.score))
            gpa = _round(sum(all_scores) / len(all_scores)) if all_scores else None
            performers.append({
                'id': student.id,
                'student_id': student.student_id,
                'full_name': student.full_name,
                'email': student.email,
                'gpa': gpa,
            })

        # Sort by GPA descending (None treated as -1 for sorting)
        performers.sort(key=lambda s: float(s['gpa']) if s['gpa'] is not None else -1, reverse=True)
        top_ten = performers[:10]

        serializer = TopPerformerSerializer(top_ten, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='course-performance')
    def course_performance(self, request):
        courses = Course.objects.prefetch_related('enrollments__grades')
        result = []

        for course in courses:
            all_scores = []
            enrolled_students = course.enrollments.count()
            for enrollment in course.enrollments.all():
                for grade in enrollment.grades.all():
                    all_scores.append(float(grade.score))
            average_score = _round(sum(all_scores) / len(all_scores)) if all_scores else None

            result.append({
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'instructor': course.instructor,
                'average_score': average_score,
                'enrolled_students': enrolled_students,
            })

        serializer = CoursePerformanceSerializer(result, many=True)
        return Response(serializer.data)
