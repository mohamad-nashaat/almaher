from .models import *
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

# Create your views here.


@login_required(login_url='login')
def person(request):
    person = Person.objects.select_related('level_id').all()
    context = {'person': person,
               }
    return render(request, 'person/person.html', context)


@login_required(login_url='login')
def edit_person(request, pk):
    level = Level.objects.all()
    person = Person.objects.get(person_id=pk)
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        father_n = request.POST['father_name']
        j = request.POST['job']
        pn = request.POST['pnumber']
        hn = request.POST['hnumber']
        ad = request.POST['address']
        bd = request.POST['bdate']
        level = request.POST['level']
        level = Level.objects.get(pk=level)
        person.first_name = fname
        person.last_name = lname
        person.father_name = father_n
        person.job = j
        person.phone_number = pn
        person.home_number = hn
        person.address = ad
        person.bdate = bd
        person.level_id = level
        person.save()
        return redirect('person')
    context = {'person': person,
               'level': level,
               }
    return render(request, 'person/edit_person.html', context)


@login_required(login_url='login')
def del_person(request, pk):
    person = Person.objects.get(person_id=pk)
    if request.method == 'POST':
        person.delete()
        return redirect('person')
    context = {'person': person,
               }
    return render(request, 'person/del_person.html', context)

# Wait List


@login_required(login_url='login')
def wait_list(request):
    person = Person.objects.select_related('level_id').filter(status=False)
    context = {'person': person,
               }
    return render(request, 'person/wait_list.html', context)

# Lock & Unlock Person


@login_required(login_url='login')
def lock_person(request, pk):
    person = Person.objects.get(person_id=pk)
    person.status = False
    person.save()
    if(person.type_id == 'Teacher'):
        return redirect('teacher')
    elif(person.type_id == 'Student'):
        return redirect('student')
    else:
        return redirect('graduate')


@login_required(login_url='login')
def unlock_person(request, pk):
    person = Person.objects.get(person_id=pk)
    person.status = True
    person.save()
    return redirect('wait_list')

# Manage Graduate


@login_required(login_url='login')
def graduate(request):
    graduate = Person.objects.select_related(
        'level_id').filter(type_id='Graduate')
    context = {'graduate': graduate,
               }
    return render(request, 'person/graduate.html', context)

# Views Teachers


@login_required(login_url='login')
def teacher(request):
    teacher = Person.objects.select_related(
        'level_id').filter(type_id='Teacher', status=True)
    c_teacher = teacher.count()
    context = {'c_teacher': c_teacher,
               'teacher': teacher,
               }
    return render(request, 'person/teacher.html', context)


@login_required(login_url='login')
def add_teacher(request):
    level = Level.objects.all()
    if request.method == 'POST':
        # Get index id
        count_index = Person.objects.all().count()
        if count_index == 0:
            count_index = 1
        else:
            count_index = Person.objects.all().aggregate(
                Max('person_id'))['person_id__max']
            count_index += 1
        fname = request.POST['fname']
        lname = request.POST['lname']
        father_n = request.POST['father_name']
        j = request.POST['job']
        pn = request.POST['pnumber']
        hn = request.POST['hnumber']
        ad = request.POST['address']
        bd = request.POST['bdate']
        level = request.POST['level']
        level = Level.objects.get(pk=level)
        Person.objects.create(person_id=count_index, type_id='Teacher', first_name=fname, last_name=lname,
                              father_name=father_n, home_number=hn, phone_number=pn,
                              job=j, address=ad, bdate=bd, level_id=level)
        messages.success(request, 'تم الاضافة بنجاح')
        return HttpResponseRedirect(reverse('add_teacher'))
    context = {'level': level,
               }
    return render(request, 'person/add_teacher.html', context)

# Views Students


@login_required(login_url='login')
def student(request):
    student = Person.objects.select_related(
        'level_id').filter(type_id='Student', status=True)
    context = {'student': student,
               }
    return render(request, 'person/student.html', context)


@login_required(login_url='login')
def add_student(request):
    level = Level.objects.all()
    if request.method == 'POST':
        count_index = Person.objects.all().count()
        if count_index == 0:
            count_index = 1
        else:
            count_index = Person.objects.all().aggregate(
                Max('person_id'))['person_id__max']
            count_index += 1
        fname = request.POST['fname']
        lname = request.POST['lname']
        father_n = request.POST['father_name']
        j = request.POST['job']
        pn = request.POST['pnumber']
        hn = request.POST['hnumber']
        ad = request.POST['address']
        bd = request.POST['bdate']
        level = request.POST['level']
        priority = request.POST['priority']
        level = Level.objects.get(pk=level)
        Person.objects.create(person_id=count_index, type_id='Student', first_name=fname, last_name=lname,
                              father_name=father_n, home_number=hn, phone_number=pn,
                              job=j, address=ad, bdate=bd, level_id=level, priority_id=priority)
        messages.success(request, 'تم الاضافة بنجاح')
        return HttpResponseRedirect(reverse('add_student'))
    context = {'level': level,
               }
    return render(request, 'person/add_student.html', context)


def set_priority(request):
    student_id = request.GET.get('student_id')
    priority_id = request.GET.get('priority_id')
    if Person.objects.filter(pk=student_id).exists():
        get_student = Person.objects.get(pk=student_id)
        get_student.priority_id = priority_id
        get_student.save()
    context = {}
    return JsonResponse(context)


def export_excel_person(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="persons.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Persons')
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['id', 'First name', 'Last name', 'Father name', 'Home number',
               'Phone number', 'Level', 'Birth date', 'Job', 'Address', 'priority', 'status']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    rows = []
    persons = Person.objects.select_related('level_id').all().order_by('pk')
    for person in persons:
        id = ''
        fname = ''
        lname = ''
        father_name = ''
        hnumber = ''
        pnumber = ''
        level = ''
        bdate = ''
        job = ''
        address = ''
        priority = ''
        status = ''
        # Check all values if none
        if person.person_id is not None:
            id = person.person_id
        if person.first_name is not None:
            fname = person.first_name
        if person.last_name is not None:
            lname = person.last_name
        if person.father_name is not None:
            father_name = person.father_name
        if person.home_number is not None:
            hnumber = person.home_number
        if person.phone_number is not None:
            pnumber = person.phone_number
        if person.level_id is not None:
            level = str(person.level_id)
        if person.bdate is not None:
            bdate = person.bdate
            bdate = bdate.strftime('%Y')
        if person.job is not None:
            job = person.job
        if person.address is not None:
            address = person.address
        if person.priority_id is not None:
            priority = person.priority_id
        if person.status is not None:
            status = str(person.status)
        vlues = [id, fname, lname, father_name, hnumber, pnumber,
                 level, bdate, job, address, priority, status]
        rows.append(vlues)
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response


def export_excel_student(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="students.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Students')
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['id', 'First name', 'Last name', 'Father name', 'Home number',
               'Phone number', 'Level', 'Birth date', 'Job', 'Address', 'priority', 'status']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    rows = []
    persons = Person.objects.select_related(
        'level_id').filter(type_id='Student').order_by('pk')
    for person in persons:
        id = ''
        fname = ''
        lname = ''
        father_name = ''
        hnumber = ''
        pnumber = ''
        level = ''
        bdate = ''
        job = ''
        address = ''
        priority = ''
        status = ''
        # Check all values if none
        if person.person_id is not None:
            id = person.person_id
        if person.first_name is not None:
            fname = person.first_name
        if person.last_name is not None:
            lname = person.last_name
        if person.father_name is not None:
            father_name = person.father_name
        if person.home_number is not None:
            hnumber = person.home_number
        if person.phone_number is not None:
            pnumber = person.phone_number
        if person.level_id is not None:
            level = str(person.level_id)
        if person.bdate is not None:
            bdate = person.bdate
            bdate = bdate.strftime('%Y')
        if person.job is not None:
            job = person.job
        if person.address is not None:
            address = person.address
        if person.priority_id is not None:
            priority = person.priority_id
        if person.status is not None:
            status = str(person.status)
        vlues = [id, fname, lname, father_name, hnumber, pnumber,
                 level, bdate, job, address, priority, status]
        rows.append(vlues)
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response


def export_excel_teacher(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="teachers.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Teachers')
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['id', 'First name', 'Last name', 'Father name', 'Home number',
               'Phone number', 'Level', 'Birth date', 'Job', 'Address', 'priority', 'status']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    rows = []
    persons = Person.objects.select_related(
        'level_id').filter(type_id='Teacher').order_by('pk')
    for person in persons:
        id = ''
        fname = ''
        lname = ''
        father_name = ''
        hnumber = ''
        pnumber = ''
        level = ''
        bdate = ''
        job = ''
        address = ''
        priority = ''
        status = ''
        # Check all values if none
        if person.person_id is not None:
            id = person.person_id
        if person.first_name is not None:
            fname = person.first_name
        if person.last_name is not None:
            lname = person.last_name
        if person.father_name is not None:
            father_name = person.father_name
        if person.home_number is not None:
            hnumber = person.home_number
        if person.phone_number is not None:
            pnumber = person.phone_number
        if person.level_id is not None:
            level = str(person.level_id)
        if person.bdate is not None:
            bdate = person.bdate
            bdate = bdate.strftime('%Y')
        if person.job is not None:
            job = person.job
        if person.address is not None:
            address = person.address
        if person.priority_id is not None:
            priority = person.priority_id
        if person.status is not None:
            status = str(person.status)
        vlues = [id, fname, lname, father_name, hnumber, pnumber,
                 level, bdate, job, address, priority, status]
        rows.append(vlues)
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response


def export_excel_graduate(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="graduates.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Graduates')
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['id', 'First name', 'Last name', 'Father name', 'Home number',
               'Phone number', 'Level', 'Birth date', 'Job', 'Address', 'priority', 'status']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    rows = []
    persons = Person.objects.select_related(
        'level_id').filter(type_id='Graduate').order_by('pk')
    for person in persons:
        id = ''
        fname = ''
        lname = ''
        father_name = ''
        hnumber = ''
        pnumber = ''
        level = ''
        bdate = ''
        job = ''
        address = ''
        priority = ''
        status = ''
        # Check all values if none
        if person.person_id is not None:
            id = person.person_id
        if person.first_name is not None:
            fname = person.first_name
        if person.last_name is not None:
            lname = person.last_name
        if person.father_name is not None:
            father_name = person.father_name
        if person.home_number is not None:
            hnumber = person.home_number
        if person.phone_number is not None:
            pnumber = person.phone_number
        if person.level_id is not None:
            level = str(person.level_id)
        if person.bdate is not None:
            bdate = person.bdate
            bdate = bdate.strftime('%Y')
        if person.job is not None:
            job = person.job
        if person.address is not None:
            address = person.address
        if person.priority_id is not None:
            priority = person.priority_id
        if person.status is not None:
            status = str(person.status)
        vlues = [id, fname, lname, father_name, hnumber, pnumber,
                 level, bdate, job, address, priority, status]
        rows.append(vlues)
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response
