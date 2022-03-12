from django.db import models

# Create your models here.

class Course(models.Model):
    course_id = models.IntegerField(primary_key=True)
    course_name = models.CharField(max_length=120, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    num_of_session = models.IntegerField(null=True)
    create_date = models.DateField(auto_now_add=True, null=True)
    def __str__(self):
        return self.course_name