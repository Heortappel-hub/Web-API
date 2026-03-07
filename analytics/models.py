from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    enrollment_date = models.DateField(auto_now_add=True)
    student_id = models.CharField(unique=True, max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.full_name} ({self.student_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Course(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    code = models.CharField(unique=True, max_length=20)
    description = models.TextField(blank=True)
    credits = models.IntegerField(default=3)
    instructor = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Enrollment(models.Model):
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_DROPPED = 'DROPPED'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_DROPPED, 'Dropped'),
    ]

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-enrollment_date']

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"


class Grade(models.Model):
    id = models.AutoField(primary_key=True)
    enrollment = models.ForeignKey(Enrollment, related_name='grades', on_delete=models.CASCADE)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    grade_letter = models.CharField(max_length=2, blank=True)
    assignment_name = models.CharField(max_length=200)
    submission_date = models.DateField(auto_now_add=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submission_date']

    def __str__(self):
        return f"{self.assignment_name}: {self.score} ({self.grade_letter})"

    def _compute_grade_letter(self, score):
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        return 'F'

    def save(self, *args, **kwargs):
        self.grade_letter = self._compute_grade_letter(float(self.score))
        super().save(*args, **kwargs)
