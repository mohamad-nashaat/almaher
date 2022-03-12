from django.db import models
from session.models import Session
from person.models import Person

# Create your models here.

class Exam(models.Model):
    exam_type = (
        ('نظري','نظري'),
        ('عملي','عملي'),
    )
    exam_time = (
        ('الامتحان الأول','الامتحان الأول'),
        ('التكميلي','التكميلي'),
        ('الاعادة','الاعادة'),
    )
    exam_id = models.IntegerField(primary_key=True)
    type_id = models.CharField(max_length=50, null=True, choices=exam_type)
    time_id = models.CharField(max_length=50, null=True, choices=exam_time)
    student_id = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)
    session_id = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    mark = models.IntegerField(null=True)
    create_date = models.DateField(auto_now_add=True, null=True)
    def __str__(self):
        return f'{self.mark}'