from django.contrib import admin
from .models import Student, Course, Enrollment, Grade


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'full_name', 'email', 'is_active', 'enrollment_date']
    search_fields = ['first_name', 'last_name', 'email', 'student_id']
    list_filter = ['is_active', 'enrollment_date']
    ordering = ['last_name', 'first_name']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'instructor', 'credits', 'is_active']
    search_fields = ['name', 'code', 'instructor']
    list_filter = ['is_active', 'credits']
    ordering = ['code']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'enrollment_date']
    search_fields = ['student__first_name', 'student__last_name', 'course__name', 'course__code']
    list_filter = ['status', 'enrollment_date']
    ordering = ['-enrollment_date']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['assignment_name', 'enrollment', 'score', 'grade_letter', 'submission_date']
    search_fields = ['assignment_name', 'enrollment__student__first_name', 'enrollment__course__name']
    list_filter = ['grade_letter', 'submission_date']
    ordering = ['-submission_date']
