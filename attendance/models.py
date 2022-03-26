from django.db import models
from session.models import Session
from person.models import Person


class Attendance(models.Model):
    attendance_id = models.IntegerField(primary_key=True)
    person_id = models.ForeignKey(
        Person, on_delete=models.CASCADE, null=True, related_name='persons_attendance')
    session_id = models.ForeignKey(
        Session, on_delete=models.CASCADE, null=True, related_name='sessions_attendance')
    day = models.DateField(null=True)
    status = models.BooleanField(null=True)
    create_date = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.day}'
