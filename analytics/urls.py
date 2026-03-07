from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet,
    CourseViewSet,
    EnrollmentViewSet,
    GradeViewSet,
    AnalyticsViewSet,
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'grades', GradeViewSet, basename='grade')

# AnalyticsViewSet uses custom actions only (no standard list/detail routes)
analytics_summary = AnalyticsViewSet.as_view({'get': 'summary'})
analytics_top_performers = AnalyticsViewSet.as_view({'get': 'top_performers'})
analytics_course_performance = AnalyticsViewSet.as_view({'get': 'course_performance'})

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/summary/', analytics_summary, name='analytics-summary'),
    path('analytics/top-performers/', analytics_top_performers, name='analytics-top-performers'),
    path('analytics/course-performance/', analytics_course_performance, name='analytics-course-performance'),
]
