import csv
import io
from rest_framework import viewsets, filters, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.db.models import Avg, Max, Min, Count
from .models import StudentPerformance, ImportBatch
from .serializers import StudentPerformanceSerializer, ImportBatchSerializer, CSVUploadSerializer, UserRegisterSerializer


class RegisterView(generics.CreateAPIView):
    """
    User Registration - POST /api/register/
    
    Creates a new user account and returns an authentication token.
    """
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'User registered successfully',
            'username': user.username,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class StudentPerformanceViewSet(viewsets.ModelViewSet):
    """
    Student Performance ViewSet - Provides CRUD and statistics endpoints.
    
    **Endpoints:**
    - GET /api/students/ - List all students (paginated)
    - POST /api/students/ - Create a new student record
    - GET /api/students/{id}/ - Retrieve a student
    - PUT /api/students/{id}/ - Update a student
    - PATCH /api/students/{id}/ - Partial update
    - DELETE /api/students/{id}/ - Delete a student
    - GET /api/students/stats/ - Get statistics
    
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

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_csv(self, request):
        """
        Upload CSV - POST /api/students/upload_csv/
        
        Uploads a CSV file and imports data with a new batch number.
        Returns the batch number for tracking.
        """
        serializer = CSVUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        csv_file = request.FILES['file']
        
        # Check file extension
        if not csv_file.name.endswith('.csv'):
            return Response({'error': 'File must be a CSV'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get next batch number
        last_batch = ImportBatch.objects.order_by('-batch_number').first()
        new_batch_number = (last_batch.batch_number + 1) if last_batch else 1
        
        # Create batch record
        batch = ImportBatch.objects.create(
            batch_number=new_batch_number,
            filename=csv_file.name
        )
        
        # Parse CSV
        try:
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            records = []
            for row in reader:
                student = StudentPerformance(
                    hours_studied=int(row.get('Hours_Studied') or 0),
                    attendance=int(row.get('Attendance') or 0),
                    parental_involvement=row.get('Parental_Involvement') or '',
                    access_to_resources=row.get('Access_to_Resources') or '',
                    extracurricular_activities=row.get('Extracurricular_Activities') or '',
                    sleep_hours=int(row.get('Sleep_Hours') or 0),
                    previous_scores=int(row.get('Previous_Scores') or 0),
                    motivation_level=row.get('Motivation_Level') or '',
                    internet_access=row.get('Internet_Access') or '',
                    tutoring_sessions=int(row.get('Tutoring_Sessions') or 0),
                    family_income=row.get('Family_Income') or '',
                    teacher_quality=row.get('Teacher_Quality') or '',
                    school_type=row.get('School_Type') or '',
                    peer_influence=row.get('Peer_Influence') or '',
                    physical_activity=int(row.get('Physical_Activity') or 0),
                    learning_disabilities=row.get('Learning_Disabilities') or '',
                    parental_education_level=row.get('Parental_Education_Level') or '',
                    distance_from_home=row.get('Distance_from_Home') or '',
                    gender=row.get('Gender') or '',
                    exam_score=int(row.get('Exam_Score') or 0),
                    batch=batch,
                )
                records.append(student)
                
                # Bulk insert every 1000 records
                if len(records) >= 1000:
                    StudentPerformance.objects.bulk_create(records)
                    records = []
            
            # Insert remaining records
            if records:
                StudentPerformance.objects.bulk_create(records)
            
            # Update batch record count
            batch.record_count = StudentPerformance.objects.filter(batch=batch).count()
            batch.save()
            
            return Response({
                'message': 'CSV imported successfully',
                'batch_number': new_batch_number,
                'record_count': batch.record_count,
                'filename': csv_file.name
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            batch.delete()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ImportBatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Import Batch ViewSet - View import batches.
    
    **Endpoints:**
    - GET /api/batches/ - List all batches
    - GET /api/batches/{id}/ - Get batch details
    - GET /api/batches/{id}/students/ - Get students in this batch
    """
    queryset = ImportBatch.objects.all().order_by('-created_at')
    serializer_class = ImportBatchSerializer
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get all students in this batch"""
        batch = self.get_object()
        students = StudentPerformance.objects.filter(batch=batch)
        serializer = StudentPerformanceSerializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for this batch"""
        batch = self.get_object()
        stats = StudentPerformance.objects.filter(batch=batch).aggregate(
            total_count=Count('id'),
            avg_score=Avg('exam_score'),
            max_score=Max('exam_score'),
            min_score=Min('exam_score'),
            avg_hours_studied=Avg('hours_studied'),
            avg_attendance=Avg('attendance'),
        )
        return Response({
            'batch_number': batch.batch_number,
            'stats': stats
        })

    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        """
        Get Analysis - GET /api/batches/{id}/analysis/
        
        Returns score distribution (per 10 points) and most impactful factors.
        """
        batch = self.get_object()
        students = StudentPerformance.objects.filter(batch=batch)
        
        if not students.exists():
            return Response({'error': 'No students in this batch'}, status=status.HTTP_404_NOT_FOUND)
        
        # Score distribution (0-9, 10-19, ..., 90-100)
        distribution = {f'{i*10}-{i*10+9}': 0 for i in range(10)}
        distribution['90-100'] = 0  # Include 100
        
        scores = list(students.values_list('exam_score', flat=True))
        for score in scores:
            if score >= 90:
                distribution['90-100'] += 1
            else:
                bucket = f'{(score // 10) * 10}-{(score // 10) * 10 + 9}'
                distribution[bucket] += 1
        
        # Calculate correlation for numeric factors
        def calculate_correlation(factor_values, score_values):
            """Calculate Pearson correlation coefficient"""
            n = len(factor_values)
            if n == 0:
                return 0
            
            mean_x = sum(factor_values) / n
            mean_y = sum(score_values) / n
            
            numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(factor_values, score_values))
            
            sum_sq_x = sum((x - mean_x) ** 2 for x in factor_values)
            sum_sq_y = sum((y - mean_y) ** 2 for y in score_values)
            
            denominator = (sum_sq_x * sum_sq_y) ** 0.5
            
            if denominator == 0:
                return 0
            return numerator / denominator
        
        # Numeric factors to analyze (excluding previous_scores as it's score-related)
        numeric_factors = ['hours_studied', 'attendance', 'sleep_hours', 
                          'tutoring_sessions', 'physical_activity']
        
        correlations = {}
        for factor in numeric_factors:
            factor_values = list(students.values_list(factor, flat=True))
            correlation = calculate_correlation(factor_values, scores)
            correlations[factor] = round(correlation, 4)
        
        # Sort by absolute correlation value
        sorted_factors = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
        
        return Response({
            'batch_number': batch.batch_number,
            'total_students': len(scores),
            'score_distribution': distribution,
            'factor_correlations': dict(sorted_factors),
            'most_impactful_factor': {
                'name': sorted_factors[0][0] if sorted_factors else None,
                'correlation': sorted_factors[0][1] if sorted_factors else None,
                'interpretation': self._interpret_correlation(sorted_factors[0][1]) if sorted_factors else None
            }
        })
    
    def _interpret_correlation(self, correlation):
        """Interpret correlation strength"""
        abs_corr = abs(correlation)
        direction = 'positive' if correlation > 0 else 'negative'
        
        if abs_corr >= 0.7:
            strength = 'strong'
        elif abs_corr >= 0.4:
            strength = 'moderate'
        elif abs_corr >= 0.2:
            strength = 'weak'
        else:
            strength = 'very weak'
        
        return f'{strength} {direction} correlation'
