from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.db.models import Max, Q, Count, Avg, Prefetch, PROTECT

import xlwt
import tempfile
from django.template.loader import render_to_string
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration
# Import models
from course.models import Course
from level.models import Level
from period.models import Time
from person.views import student
from position.models import Position
from person.models import Person
from session.models import Session, Session_Student
from exam.models import Exam
from result.models import Result
from attendance.models import Attendance

from session.tests import generate_sessions
from attendance.tests import update_attendance
from course.tests import get_request_session_course_id

# Create your views here.


@login_required(login_url='login')
def session(request):
    get_course_id = get_request_session_course_id(request)
    # Get all sessions
    session = Session.objects.select_related(
        'course_id', 'level_id', 'position_id', 'time_id', 'teacher_id').prefetch_related('session_student_set').filter(
            course_id=get_course_id).annotate(
            student_count=Count('session_student'))
    # Get all sessions that have teacher
    session_list = session.filter(
        ~Q(teacher_id=None)).values_list('session_id', flat=True)
    # Get the teacher_id that added to seesions
    in_session_teacher = Session.objects.filter(
        pk__in=session_list).values_list('teacher_id', flat=True)
    # Get all teachers that don't added to sessions
    teacher = Person.objects.filter(type_id__in=('Teacher', 'Graduate'), status=True).filter(
        ~Q(pk__in=in_session_teacher)).order_by('first_name')
    # Create a dictionary to add all details
    sessions = []
    for oneSession in session:
        # Count students in current session
        c_student = oneSession.student_count
        # Get the avrage for current session
        get_students_id = oneSession.session_student_set.values_list(
            'student_id__bdate', flat=True)
        avg_date = 0
        for per in get_students_id:
            if per is not None:
                bdate = per
                bdate = bdate.year
                avg_date += int(bdate)
        if c_student != 0:
            avg_date = int(avg_date / c_student)
        dictionary_session = {
            'session': oneSession,
            'avg_date': avg_date
        }
        sessions.append(dictionary_session)
    context = {'dictionary_session': sessions,
               'teacher': teacher,
               'get_course_id': get_course_id,
               }
    return render(request, 'session/session.html', context)


@login_required(login_url='login')
def generate_session(request):
    get_course_id = get_request_session_course_id(request)
    level = Level.objects.all().order_by('level_id').reverse()
    time = Time.objects.all()
    position = Position.objects.all()
    student_count = []
    student_count2 = []
    level_list = level.values_list('level_name', flat=True)
    for level_loop in level_list:
        l_count = Person.objects.filter(
            type_id='Student', level_id=level_loop, status=True, priority_id='مستمر').count()
        student_count.append(l_count)
    zip_list = zip(level_list, student_count)
    for level_loop in level_list:
        l_count = Person.objects.filter(
            type_id='Student', level_id=level_loop, status=True, priority_id='غير معروف').count()
        student_count2.append(l_count)
    zip_list2 = zip(level_list, student_count2)
    if request.method == 'POST':
        # Get index id session
        count_index = Session.objects.all().count()
        if count_index == 0:
            count_index = 1
        else:
            count_index = Session.objects.all().aggregate(
                Max('session_id'))['session_id__max']
            count_index += 1
        # Check session
        ch_session = Session.objects.filter(course_id=get_course_id).count()
        if ch_session == 0:
            # Loop to create sessons
            for level_loop in level_list:
                get_level = Level.objects.get(pk=level_loop)
                # Get requests
                # Get count of sutdents
                count_student_1 = int(request.POST.get(
                    f'count_student_1_{level_loop}'))
                count_student_2 = int(request.POST.get(
                    f'count_student_2_{level_loop}'))
                # Get last session number
                get_last_session_number = Session.objects.filter(
                    course_id=get_course_id).count()
                if get_last_session_number == 0:
                    get_last_session_number = 1
                else:
                    get_last_session_number = Session.objects.filter(
                        course_id=get_course_id).aggregate(Max('session_number'))['session_number__max']
                    get_last_session_number += 1
                # Get count of session for curent level
                get_count_session = int(request.POST.get(
                    f'count_session_{level_loop}'))
                get_count_session += get_last_session_number
                # Get postion
                get_position = request.POST.get(f'position_{level_loop}')
                get_position = Position.objects.get(pk=get_position)
                # Get time
                get_time = request.POST.get(f'time_{level_loop}')
                get_time = Time.objects.get(pk=get_time)
                for l1 in range(get_last_session_number, get_count_session):
                    new_session = Session(session_id=count_index, level_id=get_level, course_id=get_course_id,
                                          session_number=l1, time_id=get_time, position_id=get_position)
                    new_session.save()
                    count_index += 1
                    generate_sessions(request, count_student_1,
                                      new_session, 'مستمر')
                    generate_sessions(request, count_student_2,
                                      new_session, 'غير معروف')
        return redirect('session')
    context = {'level': level,
               'time': time,
               'position': position,
               'zip_list': zip_list,
               'zip_list2': zip_list2,
               'get_course_id': get_course_id,
               }
    return render(request, 'session/generate_session.html', context)


@login_required(login_url='login')
def add_session(request):
    level = Level.objects.all()
    position = Position.objects.all()
    time = Time.objects.all()
    get_course_id = get_request_session_course_id(request)
    count_index = Session.objects.all().count()
    if count_index == 0:
        count_index = 1
    else:
        count_index = Session.objects.all().aggregate(
            Max('session_id'))['session_id__max']
        count_index += 1
    if request.method == 'POST':
        get_snumber = request.POST['snumber']
        get_level = level.get(pk=request.POST['level'])
        get_position = position.get(pk=request.POST['position'])
        get_time = time.get(pk=request.POST['time'])
        Session.objects.create(session_id=count_index, level_id=get_level, course_id=get_course_id,
                               position_id=get_position, time_id=get_time, session_number=get_snumber)
        messages.success(request, 'تم الاضافة بنجاح')
        return HttpResponseRedirect(reverse('add_session'))
    context = {'level': level,
               'position': position,
               'time': time,
               'get_course_id': get_course_id,
               }
    return render(request, 'session/add_session.html', context)


@login_required(login_url='login')
def edit_session(request, pk):
    get_course_id = get_request_session_course_id(request)
    session = Session.objects.get(pk=pk)
    if request.method == 'POST':
        get_snumber = request.POST['snumber']
        get_teacher = request.POST['teacher']
        level = request.POST['level']
        position = request.POST['position']
        time = request.POST['time']
        # Get models
        teacher = Person.objects.get(pk=get_teacher)
        level = Level.objects.get(pk=level)
        position = Position.objects.get(pk=position)
        time = Time.objects.get(pk=time)
        #
        session.session_number = get_snumber
        session.teacher_id = teacher
        session.level_name = level
        session.time_id = time
        session.posistion = position
        session.save()
        messages.success(request, 'تم التعديل بنجاح')
        return HttpResponseRedirect(reverse('session'))
    in_session = Session.objects.all().filter(course_id=get_course_id).filter(
        ~Q(teacher_id=session.teacher_id)).values_list('teacher_id', flat=True)
    teacher = Person.objects.all().filter(type_id__in=('Teacher', 'Graduate')
                                          ).filter(~Q(pk__in=in_session)).order_by('first_name')
    course = Course.objects.all()
    context = {'session': session,
               'teacher': teacher,
               'course': course,
               'get_course_id': get_course_id,
               }
    return render(request, 'session/edit_session.html', context)


@login_required(login_url='login')
def del_session(request, pk):
    if request.user.is_staff:
        get_session = Session.objects.get(pk=pk)
        get_session.delete()
        messages.success(request, 'تم الحذف بنجاح')
        return redirect('session')
    messages.warning(request, 'ليس لديك صلاحية للقيام بهذه العملية')
    return redirect('session')


@login_required(login_url='login')
def get_session_student(request):
    get_course_id = get_request_session_course_id(request)
    session = Session.objects.filter(course_id=get_course_id)
    c_session = session.count()
    if request.method == 'POST':
        get_snumber = int(request.POST['snumber'])
        session_number = Session.objects.get(
            course_id=get_course_id, session_number=get_snumber)
        return redirect('session_student', session_number.session_id)
    return render(request, 'session/get_session_student.html', {'c_session': c_session})


@login_required(login_url='login')
def session_student(request, pk):
    get_course_id = get_request_session_course_id(request)
    session = Session.objects.filter(course_id=get_course_id)
    c_session = session.count()
    if request.method == 'POST':
        get_snumber = int(request.POST['snumber'])
        session = Session.objects.get(
            course_id=get_course_id, session_number=get_snumber)
        return redirect('session_student', session.session_id)
    elif c_session != 0:
        global new_pk
        f_session = session.first()
        l_session = session.last()
        if pk == 1:
            new_pk = f_session.session_id
        else:
            new_pk = pk
        to_next = new_pk
        to_previous = new_pk
        # set to_next & to_previous
        if new_pk == 1:
            to_next = new_pk + 1
        elif new_pk == f_session.session_id:
            to_next = new_pk + 1
        elif new_pk == l_session.session_id:
            to_previous = new_pk - 1
        else:
            to_next = new_pk + 1
            to_previous = new_pk - 1
        session = Session.objects.select_related(
            'course_id', 'level_id', 'position_id', 'time_id', 'teacher_id').get(session_id=new_pk)
        session_student = Session_Student.objects.select_related(
            'session_id', 'student_id').filter(session_id=new_pk)
        # Get student not Enrolment in sessions
        get_session = Session.objects.filter(
            course_id=get_course_id).values_list('session_id', flat=True)
        in_session = Session_Student.objects.filter(
            session_id__in=get_session).values_list('student_id', flat=True)
        # Q objects can be negated with the ~ operator
        student = Person.objects.select_related('level_id').filter(
            type_id='Student', level_id=session.level_id, status=True).filter(~Q(pk__in=in_session))
        in_session_teacher = Session.objects.all().filter(pk__in=get_session).filter(
            ~Q(teacher_id=None)).values_list('teacher_id', flat=True)
        teacher = Person.objects.select_related('level_id').filter(type_id__in=('Teacher', 'Graduate'), level_id=session.level_id, status=True).filter(
            ~Q(pk__in=in_session_teacher)).order_by('first_name')
        context = {'session': session,
                   'session_student': session_student,
                   'student': student,
                   'f_session': f_session,
                   'l_session': l_session,
                   'to_next': to_next,
                   'to_previous': to_previous,
                   'teacher': teacher,
                   'c_session': c_session,
                   'get_course_id': get_course_id,
                   }
        return render(request, 'session/session_student.html', context)
    else:
        return redirect('session')


@login_required(login_url='login')
def add_session_student(request, pk, num):
    # Set student
    count_index = Session_Student.objects.all().count()
    if count_index == 0:
        count_index = 1
    else:
        count_index = Session_Student.objects.all().aggregate(Max('id'))[
            'id__max']
        count_index += 1
    session = Session.objects.get(pk=pk)
    student = Person.objects.get(pk=num)
    Session_Student.objects.create(
        id=count_index, session_id=session, student_id=student)
    # Update attendance
    update_attendance(request, student, session)
    return redirect('session_student', pk)


@login_required(login_url='login')
def del_session_student(request, pk, num):
    get_session_student = Session_Student.objects.get(pk=num)
    get_session_student.delete()
    return redirect('session_student', pk)


@login_required(login_url='login')
def view_session_student(request):
    get_course_id = get_request_session_course_id(request)
    session = Session.objects.all().filter(
        course_id=get_course_id).values_list('session_id', flat=True)
    session_student = Session_Student.objects.select_related(
        'session_id', 'session_id__course_id', 'session_id__level_id', 'session_id__teacher_id', 'session_id__position_id', 'session_id__time_id', 'student_id').filter(session_id__in=session)
    context = {'session_student': session_student,
               'get_course_id': get_course_id,
               }
    return render(request, 'session/view_session_student.html', context)


@login_required(login_url='login')
def wait_list_session(request):
    get_course_id = get_request_session_course_id(request)
    session = Session.objects.select_related(
        'level_id').filter(course_id=get_course_id)
    get_session = session.values_list('session_id', flat=True)
    in_session = Session_Student.objects.all().filter(
        session_id__in=get_session).values_list('student_id', flat=True)
    student = Person.objects.select_related('level_id').filter(
        type_id='Student', status=True).filter(~Q(pk__in=in_session))
    context = {'student': student,
               'session': session,
               'get_course_id': get_course_id,
               }
    return render(request, 'session/wait_list_session.html', context)


def set_teacher(request):
    teacher_id = request.GET.get('teacher_id')
    session_id = request.GET.get('session_id')
    get_session = Session.objects.get(pk=session_id)
    if Person.objects.filter(pk=teacher_id).exists():
        get_teacher = Person.objects.get(pk=teacher_id)
        get_session.teacher_id = get_teacher
        # Update attendance
        update_attendance(request, get_teacher, get_session)
    else:
        get_session.teacher_id = None
    get_session.save()
    context = {}
    return JsonResponse(context)


def set_student(request):
    # Get index id session student
    count_index_s_student = Session_Student.objects.all().count()
    if count_index_s_student == 0:
        count_index_s_student = 1
    else:
        count_index_s_student = Session_Student.objects.all().aggregate(Max('id'))[
            'id__max']
        count_index_s_student += 1
    student_id = request.GET.get('student_id')
    session_id = request.GET.get('session_id')
    get_session = Session.objects.get(pk=session_id)
    if Person.objects.filter(pk=student_id).exists():
        get_student = Person.objects.get(pk=student_id)
        Session_Student.objects.create(
            id=count_index_s_student, session_id=get_session, student_id=get_student)
        count_index_s_student += 1
        # Update attendance
        update_attendance(request, get_student, get_session)
    context = {}
    return JsonResponse(context)

# Export to *


def export_teacher_student_session_pdf(request):
    if request.user.is_staff:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sessions_data.pdf"'
        response['Content-Transform-Encoding'] = 'binary'
        get_course_id = get_request_session_course_id(request)
        queryset = Session.objects.select_related('teacher_id', 'level_id', 'position_id', 'time_id').prefetch_related(Prefetch('session_student_set', queryset=Session_Student.objects.select_related('student_id'))).filter(
            course_id=get_course_id).order_by('session_id')
        ### Get previous course and results ###
        """
        previous_course = Course.objects.all()
        previous_session = Session.objects.all()
        previous_result = Result.objects.all()
        previous_course_id = int(get_course_id.course_id) - 1
        ch_previous_course = False
        if Course.objects.filter(pk=previous_course_id).exists():
            ch_previous_course = True
            previous_course = previous_course.get(pk=previous_course_id)
            previous_session = previous_session.filter(
                course_id=previous_course)
            previous_session_list = previous_session.values_list('session_id')
            previous_result = previous_result.filter(
                session_id__in=previous_session_list)
        """
        ### End get previous course and results ###
        sessions = []
        for s in queryset:
            studensts = s.session_student_set.all()
            session_dic = {'session': s, 'studensts': studensts}
            sessions.append(session_dic)
            """
            list_stud = []
            for stud in studensts:
                if previous_result.filter(student_id=stud.student_id).exists():
                    get_previous_result = previous_result.get(
                        student_id=stud.student_id)
                    get_result_type = get_previous_result.result_type
                dic_stud_result = {'student': stud, 'result': get_result_type}
                list_stud.append(dic_stud_result)
            dic_session = {'session': s, 'students': list_stud}
            sessions.append(dic_session)
            """
        context = {'sessions': sessions,
                   'course_name': get_course_id.course_name,
                   }
        html_string = render_to_string(
            'session/pdf_session_teacher_student.html', context)
        html = HTML(string=html_string)
        result = html.write_pdf()
        with tempfile.NamedTemporaryFile(delete=True) as output:
            output.write(result)
            output.flush()
            output = open(output.name, 'rb')
            response.write(output.read())
        return response
    messages.warning(request, 'ليس لديك صلاحية للقيام بهذه العملية')
    return redirect('session')


def export_students_session_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="students_session.pdf"'
    response['Content-Transform-Encoding'] = 'binary'
    get_course_id = get_request_session_course_id(request)
    session = Session.objects.filter(
        course_id=get_course_id).order_by('session_id')
    session_list = session.values_list('session_id', flat=True)
    student = Session_Student.objects.select_related('student_id', 'session_id', 'session_id__level_id').filter(
        session_id__in=session_list).order_by('student_id__first_name')
    context = {'student': student,
               'course_name': get_course_id.course_name,
               }
    html_string = render_to_string('session/pdf_session_student.html', context)
    html = HTML(string=html_string)
    result = html.write_pdf()
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())
    return response


def export_teacher_session_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="teachers_session.pdf"'
    response['Content-Transform-Encoding'] = 'binary'
    get_course_id = get_request_session_course_id(request)
    teacher = Session.objects.select_related('teacher_id', 'level_id', 'position_id').filter(
        course_id=get_course_id).order_by('session_id')
    context = {'teacher': teacher,
               'course_name': get_course_id.course_name,
               }
    html_string = render_to_string('session/pdf_session_teacher.html', context)
    html = HTML(string=html_string)
    result = html.write_pdf()
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())
    return response


def export_sessions_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="sessions_data.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Persons')
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['id', 'First name', 'Last name', 'BDate', 'Home number',
               'Phone number', 'Course', 'Session', 'Level', 'Position', 'Teacher', 'Add date']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    rows = []
    get_course_id = get_request_session_course_id(request)
    session = Session.objects.filter(
        course_id=get_course_id).order_by('session_id')
    session_list = session.values_list('session_id', flat=True)
    student = Session_Student.objects.select_related(
        'student_id', 'session_id', 'session_id__level_id', 'session_id__position_id', 'session_id__course_id', 'session_id__teacher_id').filter(session_id__in=session_list)
    for s in student:
        id = ''
        fname = ''
        lname = ''
        bdate = ''
        hnumber = ''
        pnumber = ''
        level = ''
        session = ''
        position = ''
        course = ''
        teacher = ''
        add_date = ''
        # Check all values if none
        if s.student_id.person_id is not None:
            id = s.student_id.person_id
        if s.student_id.first_name is not None:
            fname = s.student_id.first_name
        if s.student_id.last_name is not None:
            lname = s.student_id.last_name
        if s.student_id.bdate is not None:
            bdate = s.student_id.bdate
            bdate = bdate.strftime('%Y')
        if s.student_id.home_number is not None:
            hnumber = s.student_id.home_number
        if s.student_id.phone_number is not None:
            pnumber = s.student_id.phone_number
        if s.session_id.level_id is not None:
            level = str(s.session_id.level_id)
        if s.session_id.session_number is not None:
            session = s.session_id.session_number
        if s.session_id.position_id is not None:
            position = str(s.session_id.position_id)
        if s.session_id.course_id is not None:
            course = str(s.session_id.course_id)
        if s.session_id.teacher_id is not None:
            teacher = str(s.session_id.teacher_id)
        if s.create_date is not None:
            add_date = s.create_date
            add_date = add_date.strftime('%d, %B, %Y')
        vlues = [id, fname, lname, bdate, hnumber, pnumber,
                 course, session, level, position, teacher, add_date]
        rows.append(vlues)
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response
