from django.test import TestCase

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate ,login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.db.models import Max
from django.db.models import Q
import xlwt
import tempfile
from django.template.loader import render_to_string
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration
# Import models
from course.models import Course
from level.models import Level
from period.models import Time
from position.models import Position
from person.models import Person
from session.models import Session, Session_Student
from exam.models import Exam
from result.models import Result
from attendance.models import Attendance

from course.tests import chk_request_session_course_id, get_request_session_course_id

# Create your tests here.

def update_attendance(request, std_id, session_id):
    get_course_id = get_request_session_course_id(request)
    # Update attendance
    session_list = Session.objects.all().filter(course_id=get_course_id).values_list('session_id', flat=True)
    all_attendance = Attendance.objects.filter(person_id=std_id, session_id__in=session_list)
    for attendance in all_attendance:
        get_attendance = Attendance.objects.get(pk=attendance.attendance_id)
        get_attendance.session_id = session_id
        get_attendance.save()