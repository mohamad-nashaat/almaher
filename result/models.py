from django.db import models
from session.models import Session
from person.models import Person

# Create your models here.

class Result(models.Model):
    result_type = (
        ('ناجح','ناجح'),
        ('نجاح شرطي','نجاح شرطي'),
        ('إعادة','إعادة'),
    )
    result_id = models.IntegerField(primary_key=True)
    student_id = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)
    session_id = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    attendance = models.IntegerField(null=True)
    theoretical_mark = models.IntegerField(null=True)
    practical_mark = models.IntegerField(null=True)
    result = models.IntegerField(null=True)
    result_type = models.CharField(max_length=50, null=True, choices=result_type)
    create_date = models.DateField(auto_now_add=True, null=True)
    def __str__(self):
        return f'{self.result}'