from django.contrib import admin
from course.models import Course
from level.models import Level
from period.models import Time
from position.models import Position
from person.models import Person
from session.models import Session, Session_Student
from exam.models import Exam
from result.models import Result
from attendance.models import Attendance

# Register your models here.

admin.site.register(Person)
admin.site.register(Course)
admin.site.register(Session)
admin.site.register(Session_Student)
admin.site.register(Attendance)
admin.site.register(Exam)
admin.site.register(Result)
admin.site.register(Level)
admin.site.register(Time)
admin.site.register(Position)