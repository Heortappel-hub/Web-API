import csv
import os
from django.core.management.base import BaseCommand
from students.models import StudentPerformance


class Command(BaseCommand):
    help = 'Import student performance data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='StudentPerformanceFactors.csv',
            help='Path to the CSV file (default: StudentPerformanceFactors.csv)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before import'
        )

    def handle(self, *args, **options):
        csv_file = options['file']
        
        if not os.path.exists(csv_file):
            self.stderr.write(self.style.ERROR(f'File not found: {csv_file}'))
            return

        if options['clear']:
            StudentPerformance.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing data'))

        created_count = 0
        error_count = 0

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            batch = []
            batch_size = 1000
            
            for row in reader:
                try:
                    student = StudentPerformance(
                        hours_studied=int(row['Hours_Studied']),
                        attendance=int(row['Attendance']),
                        parental_involvement=row['Parental_Involvement'],
                        access_to_resources=row['Access_to_Resources'],
                        extracurricular_activities=row['Extracurricular_Activities'],
                        sleep_hours=int(row['Sleep_Hours']),
                        previous_scores=int(row['Previous_Scores']),
                        motivation_level=row['Motivation_Level'],
                        internet_access=row['Internet_Access'],
                        tutoring_sessions=int(row['Tutoring_Sessions']),
                        family_income=row['Family_Income'],
                        teacher_quality=row['Teacher_Quality'],
                        school_type=row['School_Type'],
                        peer_influence=row['Peer_Influence'],
                        physical_activity=int(row['Physical_Activity']),
                        learning_disabilities=row['Learning_Disabilities'],
                        parental_education_level=row['Parental_Education_Level'],
                        distance_from_home=row['Distance_from_Home'],
                        gender=row['Gender'],
                        exam_score=int(row['Exam_Score']),
                    )
                    batch.append(student)
                    
                    if len(batch) >= batch_size:
                        StudentPerformance.objects.bulk_create(batch)
                        created_count += len(batch)
                        batch = []
                        self.stdout.write(f'Imported {created_count} records...')
                        
                except Exception as e:
                    error_count += 1
                    self.stderr.write(self.style.ERROR(f'Error on row: {e}'))
            
            # Import remaining records
            if batch:
                StudentPerformance.objects.bulk_create(batch)
                created_count += len(batch)

        self.stdout.write(self.style.SUCCESS(
            f'Successfully imported {created_count} records. Errors: {error_count}'
        ))
