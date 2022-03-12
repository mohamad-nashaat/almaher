from django.test import TestCase

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
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

from course.tests import get_request_session_course_id

# Create your tests here.


def generate_sessions(request, count_student, new_session, priority):
    get_course_id = get_request_session_course_id(request)
    # Get index id session_student
    count_index_s_student = Session_Student.objects.all().count()
    if count_index_s_student == 0:
        count_index_s_student = 1
    else:
        count_index_s_student = Session_Student.objects.all().aggregate(Max('id'))[
            'id__max']
        count_index_s_student += 1
    # Add students => to sessions
    get_session = Session.objects.all().filter(
        course_id=get_course_id).values_list('session_id', flat=True)
    in_session = Session_Student.objects.all().filter(
        session_id__in=get_session).values_list('student_id', flat=True)
    student = Person.objects.filter(~Q(pk__in=in_session)).filter(
        type_id='Student', status=True, level_id=new_session.level_id, priority_id=priority).order_by('bdate').values_list('person_id', flat=True)
    var_num = 0
    for std in student:
        if var_num < count_student:
            # Check birth date
            c_student = Session_Student.objects.filter(
                session_id=new_session).count()
            get_person_id = Session_Student.objects.filter(
                session_id=new_session).values_list('student_id__bdate', flat=True)
            avg_date = 0
            for per in get_person_id:
                if per is not None:
                    bdate = per
                    bdate = bdate.year
                    avg_date += int(bdate)
            if c_student != 0:
                avg_date = int(avg_date / c_student)
            # Get student
            get_student = Person.objects.get(pk=std)
            get_student_bdate = 0
            if get_student.bdate is not None:
                get_student_bdate = get_student.bdate
                get_student_bdate = get_student_bdate.year
                get_student_bdate = int(get_student_bdate)
                if get_student_bdate <= 1960:
                    if (avg_date - 15) <= get_student_bdate <= (avg_date + 15):
                        Session_Student.objects.create(
                            id=count_index_s_student, session_id=new_session, student_id=get_student)
                        count_index_s_student += 1
                        var_num += 1
                    elif avg_date == 0:
                        Session_Student.objects.create(
                            id=count_index_s_student, session_id=new_session, student_id=get_student)
                        count_index_s_student += 1
                        var_num += 1
                elif get_student_bdate <= 1980:
                    if (avg_date - 8) <= get_student_bdate <= (avg_date + 8):
                        Session_Student.objects.create(
                            id=count_index_s_student, session_id=new_session, student_id=get_student)
                        count_index_s_student += 1
                        var_num += 1
                    elif avg_date == 0:
                        Session_Student.objects.create(
                            id=count_index_s_student, session_id=new_session, student_id=get_student)
                        count_index_s_student += 1
                        var_num += 1
                elif get_student_bdate <= 1990:
                    if (avg_date - 6) <= get_student_bdate <= (avg_date + 6):
                        Session_Student.objects.create(
                            id=count_index_s_student, session_id=new_session, student_id=get_student)
                        count_index_s_student += 1
                        var_num += 1
                    elif avg_date == 0:
                        Session_Student.objects.create(
                            id=count_index_s_student, session_id=new_session, student_id=get_student)
                        count_index_s_student += 1
                        var_num += 1
                elif get_student_bdate <= 2000:
                    if (avg_date - 4) <= get_student_bdate <= (avg_date + 4):
                        Session_Student.objects.create(
                            id=count_index_s_student, session_id=new_session, student_id=get_student)
                        count_index_s_student += 1
                        var_num += 1
                    elif avg_date == 0:
                        Session_Student.objects.create(
                            id=count_index_s_student, session_id=new_session, student_id=get_student)
                        count_index_s_student += 1
                        var_num += 1
                elif get_student_bdate <= 2010:
                    if (avg_date - 3) <= get_student_bdate <= (avg_date + 3):
                        Session_Student.objects.create(
                            id=count_index_s_student, session_id=new_session, student_id=get_student)
                        count_index_s_student += 1
                        var_num += 1
                    elif avg_date == 0:
                        Session_Student.objects.create(
                            id=count_index_s_student, session_id=new_session, student_id=get_student)
                        count_index_s_student += 1
                        var_num += 1
                else:
                    if (avg_date - 2) <= get_student_bdate <= (avg_date + 2):
                        Session_Student.objects.create(
                            id=count_index_s_student, session_id=new_session, student_id=get_student)
                        count_index_s_student += 1
                        var_num += 1
                    elif avg_date == 0:
                        Session_Student.objects.create(
                            id=count_index_s_student, session_id=new_session, student_id=get_student)
                        count_index_s_student += 1
                        var_num += 1
        else:
            break
