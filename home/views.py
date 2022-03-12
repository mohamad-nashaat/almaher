from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from weasyprint import HTML
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


def home(request):
    chk_login = request.user.is_authenticated
    return render(request, 'home/home.html', {'chk_login': chk_login})


@login_required(login_url='login')
def blank(request):
    return render(request, 'home/blank.html')


@login_required(login_url='login')
def pg_404(request):
    return render(request, 'home/404.html')


@login_required(login_url='login')
def dashboard(request):
    get_course_id = 0
    if chk_request_session_course_id(request):
        get_course_id = get_request_session_course_id(request)
    else:
        return redirect('select_course')
    c_teacher = Person.objects.all().filter(type_id='Teacher').count()
    c_student = Person.objects.all().filter(type_id='Student').count()
    c_graduate = Person.objects.all().filter(type_id='Graduate').count()
    c_course = Course.objects.all().count()
    session = Session.objects.filter(course_id=get_course_id)
    c_session = session.count()
    c_session_student = Session_Student.objects.filter(
        session_id__in=session).count()
    context = {'c_teacher': c_teacher,
               'c_student': c_student,
               'c_graduate': c_graduate,
               'c_course': c_course,
               'c_session': c_session,
               'c_session_student': c_session_student,
               'get_course_id': get_course_id,
               }
    return render(request, 'home/dashboard.html', context)
