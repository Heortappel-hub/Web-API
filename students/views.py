from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from django.db.models import Avg, Max, Min, Count
from django.shortcuts import render
from .models import StudentPerformance
from .serializers import StudentPerformanceSerializer


class StudentPerformanceViewSet(viewsets.ModelViewSet):
    """
    Student Performance ViewSet - Provides CRUD and statistics endpoints.
    
    Supports filtering by gender, school type, and score range.
    Supports pagination, search, and ordering.
    
    **Endpoints:**
    - GET /api/students/ - List all students (paginated)
    - POST /api/students/ - Create a new student record
    - GET /api/students/{id}/ - Retrieve a student
    - PUT /api/students/{id}/ - Update a student
    - PATCH /api/students/{id}/ - Partial update
    - DELETE /api/students/{id}/ - Delete a student
    - GET /api/students/stats/ - Get statistics
    - GET /api/students/table/ - View as HTML table
    
    **Query Parameters:**
    - gender: Filter by gender (Male/Female)
    - school_type: Filter by school type (Public/Private)
    - min_score: Minimum exam score
    - max_score: Maximum exam score
    - search: Search in gender, school_type, parental_involvement
    - ordering: Order by exam_score, hours_studied, attendance, id
    """
    queryset = StudentPerformance.objects.all()
    serializer_class = StudentPerformanceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['gender', 'school_type', 'parental_involvement']
    ordering_fields = ['exam_score', 'hours_studied', 'attendance', 'id']
    ordering = ['id']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Custom filtering
        gender = self.request.query_params.get('gender')
        school_type = self.request.query_params.get('school_type')
        min_score = self.request.query_params.get('min_score')
        max_score = self.request.query_params.get('max_score')
        
        if gender:
            queryset = queryset.filter(gender__iexact=gender)
        if school_type:
            queryset = queryset.filter(school_type__iexact=school_type)
        if min_score:
            queryset = queryset.filter(exam_score__gte=int(min_score))
        if max_score:
            queryset = queryset.filter(exam_score__lte=int(max_score))
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get Statistics - GET /api/students/stats/
        
        Returns overall statistics and breakdowns by gender and school type.
        """
        stats = StudentPerformance.objects.aggregate(
            total_count=Count('id'),
            avg_score=Avg('exam_score'),
            max_score=Max('exam_score'),
            min_score=Min('exam_score'),
            avg_hours_studied=Avg('hours_studied'),
            avg_attendance=Avg('attendance'),
        )
        
        gender_stats = StudentPerformance.objects.values('gender').annotate(
            count=Count('id'),
            avg_score=Avg('exam_score')
        )
        
        school_stats = StudentPerformance.objects.values('school_type').annotate(
            count=Count('id'),
            avg_score=Avg('exam_score')
        )
        
        return Response({
            'overall': stats,
            'by_gender': list(gender_stats),
            'by_school_type': list(school_stats),
        })

    @action(detail=False, methods=['get'], renderer_classes=[TemplateHTMLRenderer])
    def table(self, request):
        """
        HTML Table View - GET /api/students/table/
        
        Displays student data in an HTML table format.
        """
        queryset = self.get_queryset()[:100]  # Limit to 100 for display
        return Response({'students': queryset}, template_name='students/table.html')
