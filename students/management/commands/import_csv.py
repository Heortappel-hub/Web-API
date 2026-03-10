import csv
from django.core.management.base import BaseCommand
from students.models import StudentPerformance


class Command(BaseCommand):
    help = 'Import student data from CSV file'

    def handle(self, *args, **kwargs):
        csv_file_path = 'StudentPerformanceFactors.csv'
        
        # Clear existing data to avoid duplicates
        StudentPerformance.objects.all().delete()
        self.stdout.write('Cleared existing data')
        
        batch = []           # List to collect objects
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
                )
                batch.append(student)
                
                # Bulk insert when batch size is reached
                if len(batch) >= batch_size:
                    StudentPerformance.objects.bulk_create(batch)
                    self.stdout.write(f'Inserted {len(batch)} records...')
                    batch = []  # Clear the list
            
            # Insert remaining records
            if batch:
                StudentPerformance.objects.bulk_create(batch)

        total = StudentPerformance.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Done! Total: {total} records'))
