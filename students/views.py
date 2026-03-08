from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Max, Min, Count
from .models import StudentPerformance
from .serializers import StudentPerformanceSerializer


class StudentPerformanceViewSet(viewsets.ModelViewSet):
    """
        学生成绩视图集，提供CRUD和统计信息接口
        支持根据性别、学校类型和成绩范围进行筛选，支持分页和排序
    """
    queryset = StudentPerformance.objects.all()
    serializer_class = StudentPerformanceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['gender', 'school_type', 'parental_involvement']
    ordering_fields = ['exam_score', 'hours_studied', 'attendance', 'id']
    ordering = ['id']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 自定义筛选
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
        """获取统计信息 GET /api/students/stats/"""
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
