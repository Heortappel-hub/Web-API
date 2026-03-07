from django.db import models


class StudentPerformance(models.Model):
	hours_studied = models.IntegerField()
	attendance = models.IntegerField()
	parental_involvement = models.CharField(max_length=10)
	access_to_resources = models.CharField(max_length=10)
	extracurricular_activities = models.CharField(max_length=3)
	sleep_hours = models.IntegerField()
	previous_scores = models.IntegerField()
	motivation_level = models.CharField(max_length=10)
	internet_access = models.CharField(max_length=3)
	tutoring_sessions = models.IntegerField()
	family_income = models.CharField(max_length=10)
	teacher_quality = models.CharField(max_length=10)
	school_type = models.CharField(max_length=10)
	peer_influence = models.CharField(max_length=10)
	physical_activity = models.IntegerField()
	learning_disabilities = models.CharField(max_length=3)
	parental_education_level = models.CharField(max_length=20)
	distance_from_home = models.CharField(max_length=10)
	gender = models.CharField(max_length=10)
	exam_score = models.IntegerField()

	class Meta:
		db_table = 'student_performance_factors'

	def __str__(self):
		return f"StudentPerformance #{self.pk} - Score: {self.exam_score}"
