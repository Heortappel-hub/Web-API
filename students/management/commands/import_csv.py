import csv
from django.core.management.base import BaseCommand
from students.models import StudentPerformance, ImportBatch


class Command(BaseCommand):
    help = 'Import student data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='StudentPerformanceFactors.csv',
                            help='Path to CSV file')
        parser.add_argument('--clear', action='store_true',
                            help='Clear all existing data before import')

    def handle(self, *args, **options):
        csv_file_path = options['file']
        
        # Optionally clear existing data
        if options['clear']:
            StudentPerformance.objects.all().delete()
            ImportBatch.objects.all().delete()
            self.stdout.write('Cleared all existing data')
        
        # Get next batch number
        last_batch = ImportBatch.objects.order_by('-batch_number').first()
        new_batch_number = (last_batch.batch_number + 1) if last_batch else 1
        
        # Create batch record
        batch = ImportBatch.objects.create(
            batch_number=new_batch_number,
            filename=csv_file_path
        )
        self.stdout.write(f'Created batch #{new_batch_number}')
        
        records = []         # List to collect objects
        batch_size = 1000    # Number of records per bulk insert

        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Create object without saving to database
                student = StudentPerformance(
                    hours_studied=int(row['Hours_Studied'] or 0),
                    attendance=int(row['Attendance'] or 0),
                    parental_involvement=row['Parental_Involvement'] or '',
                    access_to_resources=row['Access_to_Resources'] or '',
                    extracurricular_activities=row['Extracurricular_Activities'] or '',
                    sleep_hours=int(row['Sleep_Hours'] or 0),
                    previous_scores=int(row['Previous_Scores'] or 0),
                    motivation_level=row['Motivation_Level'] or '',
                    internet_access=row['Internet_Access'] or '',
                    tutoring_sessions=int(row['Tutoring_Sessions'] or 0),
                    family_income=row['Family_Income'] or '',
                    teacher_quality=row['Teacher_Quality'] or '',
                    school_type=row['School_Type'] or '',
                    peer_influence=row['Peer_Influence'] or '',
                    physical_activity=int(row['Physical_Activity'] or 0),
                    learning_disabilities=row['Learning_Disabilities'] or '',
                    parental_education_level=row['Parental_Education_Level'] or '',
                    distance_from_home=row['Distance_from_Home'] or '',
                    gender=row['Gender'] or '',
                    exam_score=int(row['Exam_Score'] or 0),
                    batch=batch,
                )
                records.append(student)
                
                # Bulk insert when batch size is reached
                if len(records) >= batch_size:
                    StudentPerformance.objects.bulk_create(records)
                    self.stdout.write(f'Inserted {len(records)} records...')
                    records = []  # Clear the list
            
            # Insert remaining records
            if records:
                StudentPerformance.objects.bulk_create(records)

        # Update batch record count
        batch.record_count = StudentPerformance.objects.filter(batch=batch).count()
        batch.save()

        self.stdout.write(self.style.SUCCESS(
            f'Done! Batch #{new_batch_number}: {batch.record_count} records imported'
        ))
