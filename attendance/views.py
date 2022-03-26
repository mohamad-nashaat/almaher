from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.db.models import Max, Q, Prefetch
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


@login_required(login_url='login')
def select_attendance(request):
    get_course_id = get_request_session_course_id(request)
    course = Course.objects.all()
    if request.method == 'POST':
        get_type = request.POST['type']
        request.session['attendance_type'] = get_type
        if get_type == '1':
            return redirect('attendance_teacher')
        else:
            return redirect('attendance_student')
    context = {'course': course,
               'get_course_id': get_course_id,
               }
    return render(request, 'attendance/attendance_select_course.html', context)


@login_required(login_url='login')
def attendance_generater(request):
    get_course_id = get_request_session_course_id(request)
    # Get data from form
    get_sdate = get_course_id.start_date
    get_num = get_course_id.num_of_session
    new_date = []
    for i in range(get_num):
        new_date.append(get_sdate)
        get_sdate = get_sdate + timedelta(days=7)
    # Get course id
    session = Session.objects.filter(course_id=get_course_id)
    session_list = session.values_list('session_id', flat=True)
    # Check if teacher or student are in attendance
    person_in_attandance = Attendance.objects.filter(
        session_id__in=session_list).values_list('person_id', flat=True)
    ###
    #person_list = Person.objects.all().values_list('person_id' ,flat=True)
    teacher = session.filter(~Q(teacher_id_id=None)).filter(
        ~Q(teacher_id__in=person_in_attandance)).values_list('teacher_id', flat=True)
    session_student = Session_Student.objects.filter(
        session_id__in=session_list)
    student = session_student.filter(
        ~Q(student_id__in=person_in_attandance)).values_list('student_id', flat=True)
    ###
    # Add teacher to attendance
    for item in teacher:
        get_teacher = Person.objects.get(pk=item)
        get_session = session.get(teacher_id=get_teacher)
        count_index = Attendance.objects.all().count()
        if count_index == 0:
            count_index = 1
        else:
            count_index = Attendance.objects.all().aggregate(
                Max('attendance_id'))['attendance_id__max']
            count_index += 1
        for x in range(get_num):
            Attendance.objects.create(attendance_id=count_index, person_id=get_teacher,
                                      session_id=get_session, day=new_date[x], status=False)
            count_index += 1
    # Add student to attendance
    for item in student:
        get_student = Person.objects.get(pk=item)
        get_session_student = session_student.get(student_id=get_student)
        count_index = Attendance.objects.all().count()
        if count_index == 0:
            count_index = 1
        else:
            count_index = Attendance.objects.all().aggregate(
                Max('attendance_id'))['attendance_id__max']
            count_index += 1
        for x in range(get_num):
            Attendance.objects.create(attendance_id=count_index, person_id=get_student,
                                      session_id=get_session_student.session_id, day=new_date[x], status=False)
            count_index += 1
    messages.success(request, 'تم الانشاء بنجاح')
    return HttpResponseRedirect(reverse('attendance'))


@login_required(login_url='login')
def attendance_teacher(request):
    get_course_id = get_request_session_course_id(request)
    session = Session.objects.filter(course_id=get_course_id)
    sessions = session.values_list('session_id', flat=True)
    persons = session.values_list('teacher_id', flat=True)
    persons = Person.objects.filter(
        pk__in=persons).prefetch_related(
            Prefetch(
                'persons_attendance', queryset=Attendance.objects.filter(
                    session_id__in=sessions).order_by('day').select_related('session_id')
            ),
            Prefetch(
                'teachers', queryset=Session.objects.filter(pk__in=sessions, teacher_id__in=persons))
    )
    day_attendance = Attendance.objects.all().filter(person_id__in=persons,
                                                     session_id__in=sessions).values_list('day', flat=True).order_by('day').distinct()
    attendances = []
    for person in persons:
        session_num = person.teachers.all()
        session_num = list(session_num)
        session_num = session_num[0].session_number
        attendance = person.persons_attendance.all()
        dic_attendance = {
            'person': person,
            'session_num': session_num,
            'attendance': attendance
        }
        attendances.append(dic_attendance)
    context = {'day_attendance': day_attendance,
               'attendances': attendances,
               'get_course_id': get_course_id,
               }
    return render(request, 'attendance/attendance_teacher.html', context)


@login_required(login_url='login')
def attendance_student(request):
    get_course_id = get_request_session_course_id(request)
    session = Session.objects.filter(course_id=get_course_id)
    sessions = session.values_list('session_id', flat=True)
    persons = Session_Student.objects.filter(
        session_id__in=sessions).values_list('student_id', flat=True)
    persons = Person.objects.filter(
        pk__in=persons).prefetch_related(
            Prefetch(
                'persons_attendance', queryset=Attendance.objects.filter(
                    session_id__in=sessions).order_by('day').select_related('session_id')
            ),
            Prefetch(
                'students', queryset=Session_Student.objects.filter(session_id__in=sessions,
                                                                    student_id__in=persons).select_related('session_id'))
    )
    day_attendance = Attendance.objects.all().filter(person_id__in=persons,
                                                     session_id__in=sessions).values_list('day', flat=True).order_by('day').distinct()
    attendances = []
    for person in persons:
        session_num = person.students.all()
        session_num = list(session_num)
        session_num = session_num[0].session_id.session_number
        attendance = person.persons_attendance.all()
        dic_attendance = {
            'person': person,
            'session_num': session_num,
            'attendance': attendance
        }
        attendances.append(dic_attendance)
    context = {'day_attendance': day_attendance,
               'attendances': attendances,
               'get_course_id': get_course_id,
               }
    return render(request, 'attendance/attendance_student.html', context)


def change_status_true(request):
    attendance_id = request.GET.get('attendance_id')
    attendance = Attendance.objects.get(pk=attendance_id)
    attendance.status = True
    attendance.save()
    context = {}
    return JsonResponse(context)


def change_status_false(request):
    attendance_id = request.GET.get('attendance_id')
    attendance = Attendance.objects.get(pk=attendance_id)
    attendance.status = False
    attendance.save()
    context = {}
    return JsonResponse(context)


def export_excel_attendance(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="attendance.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Students')
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    ###
    get_course_id = get_request_session_course_id(request)
    session_list = Session.objects.filter(
        course_id=get_course_id).values_list('session_id', flat=True)
    day_attendance = Attendance.objects.all().filter(
        session_id__in=session_list).order_by('day').distinct('day')
    columns = ['id', 'First name', 'Last name', 'BDate',
               'Phone number', 'Type', 'Priority', 'Session', 'Level']
    for day in day_attendance:
        get_day = day.day
        get_day = get_day.strftime('%m/%d/%Y')
        columns.append(get_day)
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    rows = []
    ###
    teacher = Session.objects.filter(
        session_id__in=session_list).values_list('teacher_id', flat=True)
    student = Session_Student.objects.filter(
        session_id__in=session_list).values_list('student_id', flat=True)
    get_attendance = Attendance.objects.filter(
        session_id__in=session_list, person_id__in=teacher).select_related(
            'person_id', 'session_id', 'session_id__level_id').distinct('person_id') | Attendance.objects.filter(
            session_id__in=session_list, person_id__in=student).select_related(
                'person_id', 'session_id', 'session_id__level_id').distinct('person_id')
    for all_person in get_attendance:
        status_attendance = Attendance.objects.all().filter(
            person_id=all_person.person_id, session_id__in=session_list).order_by('day')
        id = ''
        fname = ''
        lname = ''
        bdate = ''
        phone_number = ''
        type_person = ''
        priority = ''
        session = ''
        level = ''
        # Check all values if none
        if all_person.person_id.person_id is not None:
            id = all_person.person_id.person_id
        if all_person.person_id.first_name is not None:
            fname = all_person.person_id.first_name
        if all_person.person_id.last_name is not None:
            lname = all_person.person_id.last_name
        if all_person.person_id.bdate is not None:
            bdate = all_person.person_id.bdate
            bdate = bdate.strftime('%Y')
        if all_person.person_id.phone_number is not None:
            phone_number = all_person.person_id.phone_number
        if all_person.person_id.type_id is not None:
            type_person = all_person.person_id.type_id
        if all_person.person_id.priority_id is not None:
            priority = all_person.person_id.priority_id
        if all_person.session_id.session_number is not None:
            session = all_person.session_id.session_number
        if all_person.session_id.level_id is not None:
            level = str(all_person.session_id.level_id)
        # Enter values
        value = [id, fname, lname, bdate, phone_number,
                 type_person, priority, session, level]
        for st in status_attendance:
            status = str(False)
            if st.status is not None:
                status = str(st.status)
            value.append(status)
        rows.append(value)
    ###
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response


def export_attendance_student_pdf(request):
    if request.user.is_staff:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="attendance_student.pdf"'
        response['Content-Transform-Encoding'] = 'binary'
        get_course_id = get_request_session_course_id(request)
        sessions = Session.objects.filter(
            course_id=get_course_id).order_by('session_id').select_related(
            'course_id', 'level_id', 'position_id', 'time_id', 'teacher_id').prefetch_related('sessions', 'sessions__student_id')
        session_list = sessions.values_list('session_id', flat=True)
        # Check if attendance is 0
        chk_attendance = Attendance.objects.filter(
            session_id__in=session_list).distinct('person_id').count()
        if chk_attendance == 0:
            messages.error(request, 'الرجاء انشاء الحضور اولا')
            return HttpResponseRedirect(reverse('attendance'))
        day = Attendance.objects.filter(session_id__in=session_list).order_by(
            'day').distinct('day').values_list('day', flat=True)
        new_day = []
        for d in day:
            new_day.append(d)
            if len(new_day) == 3:
                new_day.append('تقييم 1')
            elif len(new_day) == 8:
                new_day.append('تقييم 2')
            elif len(new_day) == 14:
                new_day.append('تقييم 3')
        day = new_day
        # Get session number
        num_of_session = get_course_id.num_of_session
        num_of_session_list = []
        for i in range(num_of_session):
            num_of_session_list.append(i)
        last_session = []
        for session in sessions:
            get_session_students = session.sessions.all()
            list_students = []
            for student in get_session_students:
                get_attendance = Attendance.objects.filter(
                    session_id__in=session_list, person_id=student.student_id).order_by('day')
                new_attend = []
                for atend in get_attendance:
                    new_attend.append(atend)
                    if len(new_attend) == 3:
                        new_attend.append('')
                    elif len(new_attend) == 8:
                        new_attend.append('')
                    elif len(new_attend) == 14:
                        new_attend.append('')
                dic_student = {'student': student, 'attendance': new_attend}
                list_students.append(dic_student)
            dic_sessions_students = {
                'session': session, 'student': list_students}
            last_session.append(dic_sessions_students)
        context = {'last_session': last_session,
                   'num_of_session_list': num_of_session_list,
                   'course_name': get_course_id.course_name,
                   'day': day,
                   }
        html_string = render_to_string(
            'attendance/pdf_attendance_student.html', context)
        html = HTML(string=html_string)
        result = html.write_pdf()
        with tempfile.NamedTemporaryFile(delete=True) as output:
            output.write(result)
            output.flush()
            output = open(output.name, 'rb')
            response.write(output.read())
        return response
    messages.warning(request, 'ليس لديك صلاحية للقيام بهذه العملية')
    return redirect('attendance')


def export_attendance_teacher_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance_teacher.pdf"'
    response['Content-Transform-Encoding'] = 'binary'
    get_course_id = get_request_session_course_id(request)
    sessions = Session.objects.filter(
        course_id=get_course_id).order_by('session_id').select_related(
        'course_id', 'level_id', 'position_id', 'time_id', 'teacher_id')
    session_list = sessions.values_list('session_id', flat=True)
    # Check if attendance is 0
    chk_attendance = Attendance.objects.filter(
        session_id__in=session_list).distinct('person_id').count()
    if chk_attendance == 0:
        messages.error(request, 'الرجاء انشاء الحضور اولا')
        return HttpResponseRedirect(reverse('attendance'))
    day = Attendance.objects.filter(session_id__in=session_list).order_by(
        'day').distinct('day').values_list('day', flat=True)
    teacher = Session.objects.filter(session_id__in=session_list).order_by(
        'teacher_id').values_list('teacher_id', flat=True)
    get_attendance = Attendance.objects.filter(
        session_id__in=session_list, person_id__in=teacher).order_by('session_id').distinct('session_id')
    last_attendance = []
    for all_person in get_attendance:
        status_attendance = Attendance.objects.filter(
            person_id=all_person.person_id, session_id__in=session_list).order_by('day')
        dic_teacher = {'teacher': all_person, 'attendance': status_attendance}
        last_attendance.append(dic_teacher)
    context = {'day': day,
               'last_attendance': last_attendance,
               'course_name': get_course_id.course_name,
               }
    html_string = render_to_string(
        'attendance/pdf_attendance_teacher.html', context)
    html = HTML(string=html_string)
    result = html.write_pdf()
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())
    return response
