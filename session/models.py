from django.db import models
from course.models import Course
from level.models import Level
from period.models import Time
from position.models import Position
from person.models import Person

# Create your models here.


class Session(models.Model):
    session_id = models.IntegerField(primary_key=True)
    session_number = models.IntegerField(null=True)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    level_id = models.ForeignKey(Level, on_delete=models.CASCADE, null=True)
    position_id = models.ForeignKey(
        Position, on_delete=models.CASCADE, null=True)
    time_id = models.ForeignKey(Time, on_delete=models.CASCADE, null=True)
    teacher_id = models.ForeignKey(
        Person, null=True, on_delete=models.CASCADE, related_name='teachers')
    create_date = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.session_id}'


class Session_Student(models.Model):
    id = models.IntegerField(primary_key=True)
    session_id = models.ForeignKey(
        Session, on_delete=models.CASCADE, null=True, related_name='sessions')
    student_id = models.ForeignKey(
        Person, on_delete=models.CASCADE, null=True, related_name='students')
    create_date = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.id}'
