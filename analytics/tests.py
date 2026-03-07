from decimal import Decimal
from django.test import TestCase
from django.db import IntegrityError
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Student, Course, Enrollment, Grade


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

def make_student(student_id='S001', first_name='Alice', last_name='Smith',
                 email='alice@example.com', date_of_birth='2000-01-15'):
    return Student.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        date_of_birth=date_of_birth,
        student_id=student_id,
    )


def make_course(code='CS101', name='Intro to CS', instructor='Dr. Jones'):
    return Course.objects.create(code=code, name=name, instructor=instructor)


def make_enrollment(student, course, status=Enrollment.STATUS_ACTIVE):
    return Enrollment.objects.create(student=student, course=course, status=status)


def make_grade(enrollment, score, assignment_name='Midterm'):
    return Grade.objects.create(enrollment=enrollment, score=score, assignment_name=assignment_name)


# ===========================================================================
# Model Tests
# ===========================================================================

class StudentModelTest(TestCase):
    def test_student_creation(self):
        student = make_student()
        self.assertEqual(student.first_name, 'Alice')
        self.assertEqual(student.last_name, 'Smith')
        self.assertTrue(student.is_active)

    def test_full_name_property(self):
        student = make_student(first_name='Bob', last_name='Jones')
        self.assertEqual(student.full_name, 'Bob Jones')

    def test_student_str(self):
        student = make_student(student_id='S999', first_name='Jane', last_name='Doe')
        self.assertIn('S999', str(student))
        self.assertIn('Jane Doe', str(student))

    def test_unique_email(self):
        make_student(student_id='S001', email='unique@example.com')
        with self.assertRaises(Exception):
            make_student(student_id='S002', email='unique@example.com')

    def test_unique_student_id(self):
        make_student(student_id='DUP01', email='a@example.com')
        with self.assertRaises(Exception):
            make_student(student_id='DUP01', email='b@example.com')


class GradeModelTest(TestCase):
    def setUp(self):
        self.student = make_student()
        self.course = make_course()
        self.enrollment = make_enrollment(self.student, self.course)

    def _grade(self, score):
        return Grade(enrollment=self.enrollment, score=score, assignment_name='Test')

    def test_grade_letter_A(self):
        g = self._grade(95)
        g.save()
        self.assertEqual(g.grade_letter, 'A')

    def test_grade_letter_B(self):
        g = self._grade(85)
        g.save()
        self.assertEqual(g.grade_letter, 'B')

    def test_grade_letter_C(self):
        g = self._grade(75)
        g.save()
        self.assertEqual(g.grade_letter, 'C')

    def test_grade_letter_D(self):
        g = self._grade(65)
        g.save()
        self.assertEqual(g.grade_letter, 'D')

    def test_grade_letter_F(self):
        g = self._grade(50)
        g.save()
        self.assertEqual(g.grade_letter, 'F')

    def test_grade_letter_boundaries(self):
        for score, expected in [(90, 'A'), (80, 'B'), (70, 'C'), (60, 'D'), (59, 'F')]:
            g = Grade(enrollment=self.enrollment, score=score, assignment_name=f'Test{score}')
            g.save()
            self.assertEqual(g.grade_letter, expected, f"score={score}")


class EnrollmentModelTest(TestCase):
    def setUp(self):
        self.student = make_student()
        self.course = make_course()

    def test_enrollment_creation(self):
        e = make_enrollment(self.student, self.course)
        self.assertEqual(e.status, Enrollment.STATUS_ACTIVE)

    def test_unique_together_constraint(self):
        make_enrollment(self.student, self.course)
        with self.assertRaises(Exception):
            make_enrollment(self.student, self.course)


# ===========================================================================
# API Tests
# ===========================================================================

class StudentAPITest(APITestCase):
    def setUp(self):
        self.student = make_student()
        self.url_list = '/api/students/'
        self.url_detail = f'/api/students/{self.student.id}/'

    def test_list_students(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_create_student(self):
        payload = {
            'first_name': 'Charlie',
            'last_name': 'Brown',
            'email': 'charlie@example.com',
            'date_of_birth': '1999-06-20',
            'student_id': 'S100',
        }
        response = self.client.post(self.url_list, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'charlie@example.com')

    def test_retrieve_student(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['student_id'], self.student.student_id)

    def test_update_student(self):
        response = self.client.patch(self.url_detail, {'first_name': 'Updated'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')

    def test_delete_student(self):
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_full_name_in_response(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.data['full_name'], self.student.full_name)

    def test_search_by_email(self):
        response = self.client.get(self.url_list, {'search': self.student.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class StudentPerformanceAPITest(APITestCase):
    def setUp(self):
        self.student = make_student()
        self.course = make_course()
        self.enrollment = make_enrollment(self.student, self.course)
        make_grade(self.enrollment, 85, 'Assignment 1')
        make_grade(self.enrollment, 95, 'Assignment 2')
        self.url = f'/api/students/{self.student.id}/performance/'

    def test_performance_endpoint_status(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_performance_has_overall_gpa(self):
        response = self.client.get(self.url)
        self.assertIn('overall_gpa', response.data)
        self.assertIsNotNone(response.data['overall_gpa'])

    def test_performance_gpa_value(self):
        response = self.client.get(self.url)
        # Average of 85 and 95 = 90.00
        self.assertEqual(Decimal(str(response.data['overall_gpa'])), Decimal('90.00'))

    def test_performance_enrollment_list(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['enrollments']), 1)
        self.assertEqual(response.data['enrollments'][0]['course_code'], self.course.code)

    def test_performance_no_grades(self):
        student2 = make_student(student_id='S002', email='s2@example.com')
        course2 = make_course(code='MA101', name='Math')
        make_enrollment(student2, course2)
        url = f'/api/students/{student2.id}/performance/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['overall_gpa'])


class CourseAPITest(APITestCase):
    def setUp(self):
        self.course = make_course()
        self.url_list = '/api/courses/'
        self.url_detail = f'/api/courses/{self.course.id}/'

    def test_list_courses(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_course(self):
        payload = {
            'name': 'Data Structures',
            'code': 'CS201',
            'instructor': 'Dr. Smith',
            'credits': 4,
        }
        response = self.client.post(self.url_list, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_course(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], self.course.code)

    def test_search_by_instructor(self):
        response = self.client.get(self.url_list, {'search': self.course.instructor})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)


class CourseStatisticsAPITest(APITestCase):
    def setUp(self):
        self.course = make_course()
        student = make_student()
        enrollment = make_enrollment(student, self.course)
        make_grade(enrollment, 92, 'Quiz 1')
        make_grade(enrollment, 78, 'Quiz 2')
        self.url = f'/api/courses/{self.course.id}/statistics/'

    def test_statistics_status(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_statistics_fields(self):
        response = self.client.get(self.url)
        for field in ['student_count', 'average_score', 'grade_distribution']:
            self.assertIn(field, response.data)

    def test_statistics_student_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data['student_count'], 1)

    def test_statistics_grade_distribution(self):
        response = self.client.get(self.url)
        dist = response.data['grade_distribution']
        # 92 -> A, 78 -> C
        self.assertEqual(dist['A'], 1)
        self.assertEqual(dist['C'], 1)
        self.assertEqual(dist['B'], 0)


class EnrollmentAPITest(APITestCase):
    def setUp(self):
        self.student = make_student()
        self.course = make_course()
        self.enrollment = make_enrollment(self.student, self.course)
        self.url_list = '/api/enrollments/'
        self.url_detail = f'/api/enrollments/{self.enrollment.id}/'

    def test_list_enrollments(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_enrollment(self):
        student2 = make_student(student_id='S002', email='s2@example.com')
        payload = {'student': student2.id, 'course': self.course.id}
        response = self.client.post(self.url_list, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_filter_by_status(self):
        response = self.client.get(self.url_list, {'status': 'ACTIVE'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data['results']:
            self.assertEqual(item['status'], 'ACTIVE')

    def test_nested_student_and_course_in_response(self):
        response = self.client.get(self.url_detail)
        self.assertIn('student_detail', response.data)
        self.assertIn('course_detail', response.data)


class GradeAPITest(APITestCase):
    def setUp(self):
        self.student = make_student()
        self.course = make_course()
        self.enrollment = make_enrollment(self.student, self.course)
        self.grade = make_grade(self.enrollment, 88)
        self.url_list = '/api/grades/'
        self.url_detail = f'/api/grades/{self.grade.id}/'

    def test_list_grades(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_grade(self):
        payload = {
            'enrollment': self.enrollment.id,
            'score': '72.50',
            'assignment_name': 'Final Exam',
        }
        response = self.client.post(self.url_list, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['grade_letter'], 'C')

    def test_filter_by_enrollment(self):
        response = self.client.get(self.url_list, {'enrollment': self.enrollment.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class AnalyticsSummaryAPITest(APITestCase):
    def setUp(self):
        self.student = make_student()
        self.course = make_course()
        self.enrollment = make_enrollment(self.student, self.course)
        make_grade(self.enrollment, 80)
        self.url = '/api/analytics/summary/'

    def test_summary_status(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_summary_fields(self):
        response = self.client.get(self.url)
        for field in ['total_students', 'total_courses', 'total_enrollments', 'overall_average_score']:
            self.assertIn(field, response.data)

    def test_summary_counts(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data['total_students'], 1)
        self.assertEqual(response.data['total_courses'], 1)
        self.assertEqual(response.data['total_enrollments'], 1)

    def test_summary_average_score(self):
        response = self.client.get(self.url)
        self.assertEqual(Decimal(str(response.data['overall_average_score'])), Decimal('80.00'))


class TopPerformersAPITest(APITestCase):
    def setUp(self):
        # Create two students with different GPAs
        self.s1 = make_student(student_id='S001', email='s1@example.com', first_name='High', last_name='Achiever')
        self.s2 = make_student(student_id='S002', email='s2@example.com', first_name='Low', last_name='Scorer')
        course = make_course()
        e1 = make_enrollment(self.s1, course)
        course2 = make_course(code='CS999', name='Other')
        e2 = make_enrollment(self.s2, course2)
        make_grade(e1, 95)
        make_grade(e2, 60)
        self.url = '/api/analytics/top-performers/'

    def test_top_performers_status(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_top_performers_ordering(self):
        response = self.client.get(self.url)
        data = response.data
        self.assertGreaterEqual(len(data), 2)
        # First performer should have higher GPA
        self.assertGreaterEqual(
            Decimal(str(data[0]['gpa'])),
            Decimal(str(data[1]['gpa'])),
        )

    def test_top_performers_fields(self):
        response = self.client.get(self.url)
        self.assertIn('gpa', response.data[0])
        self.assertIn('full_name', response.data[0])

    def test_top_performers_max_ten(self):
        response = self.client.get(self.url)
        self.assertLessEqual(len(response.data), 10)
