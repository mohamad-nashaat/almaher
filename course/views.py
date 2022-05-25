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


@login_required(login_url='login')
def course(request):
    course = Course.objects.all()
    context = {'course': course,
               }
    return render(request, 'course/course.html', context)


@login_required(login_url='login')
def add_course(request):
    if request.method == 'POST':
        count_index = Course.objects.all().count()
        if count_index == 0:
            count_index = 1
        else:
            count_index = Course.objects.all().aggregate(
                Max('course_id'))['course_id__max']
            count_index += 1
        ncourse = request.POST['ncourse']
        sdate = request.POST['sdate']
        edate = request.POST['edate']
        count_of_session = request.POST['count_of_session']
        Course.objects.create(course_id=count_index,
                              course_name=ncourse,
                              start_date=sdate,
                              end_date=edate,
                              num_of_session=count_of_session)
        messages.success(request, 'تم الاضافة بنجاح')
        return HttpResponseRedirect(reverse('course'))
    context = {}
    return render(request, 'course/add_course.html', context)


# @login_required(login_url='login')
# def del_course(request, pk):
#     if request.user.is_staff:
#         get_course = Course.objects.get(pk=pk)
#         get_course.delete()
#         messages.success(request, 'تم الحذف بنجاح')
#         return redirect('course')
#     messages.warning(request, 'ليس لديك صلاحية للقيام بهذه العملية')
#     return redirect('course')


@login_required(login_url='login')
def select_course(request):
    # Check if course equal zero
    ch_course = Course.objects.count()
    if ch_course < 1:
        return redirect('add_course')
    elif request.method == 'POST':
        get_course = request.POST['course']
        get_course = Course.objects.get(pk=get_course)
        # Set session course_id
        request.session['get_course_id'] = get_course.course_id
        return redirect('dashboard')
    course = Course.objects.all().order_by('pk')
    context = {'course': course,
               }
    return render(request, 'course/select_course.html', context)
