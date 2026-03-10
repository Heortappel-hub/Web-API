import csv
from django.core.management.base import BaseCommand
from students.models import StudentPerformance


class Command(BaseCommand):
    help = 'Import student data from CSV file'

    def handle(self, *args, **kwargs):
        csv_file_path = 'StudentPerformanceFactors.csv'
        created = 0
        errors = 0

        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    StudentPerformance.objects.create(
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
                    created += 1
                except Exception as e:
                    errors += 1
                    self.stdout.write(self.style.ERROR(f'Error: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Done! Created: {created}, Errors: {errors}'))
