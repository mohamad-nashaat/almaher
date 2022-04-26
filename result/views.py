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


@login_required(login_url='login')
def result(request):
    get_course_id = get_request_session_course_id(request)
    in_session = Session.objects.filter(
        course_id=get_course_id).values_list('session_id', flat=True)
    result = Result.objects.filter(
        session_id__in=in_session).select_related(
            'student_id', 'session_id', 'session_id__course_id', 'session_id__level_id')
    context = {'result': result,
               'get_course_id': get_course_id,
               }
    return render(request, 'result/result.html', context)

# Generate exam for all students


@login_required(login_url='login')
def generate_result(request):
    get_course_id = get_request_session_course_id(request)
    session = Session.objects.all().filter(course_id=get_course_id)
    session_list = session.values_list('session_id', flat=True)
    # Check if student are in result
    result = Result.objects.filter(session_id__in=session_list)
    person_in_result = result.values_list('student_id', flat=True)
    session_student = Session_Student.objects.all().filter(session_id__in=session_list)
    student = session_student.filter(
        ~Q(student_id__in=person_in_result)).values_list('student_id', flat=True)
    # Check if any student is not in exam
    session_student_count = session_student.values_list(
        'student_id', flat=True).distinct('student_id')
    chk_exam = Exam.objects.filter(session_id__in=session_list).values_list(
        'student_id', flat=True).distinct('student_id')
    if len(session_student_count) != len(chk_exam):
        messages.error(request, 'الرجاء انشاء الاختبارات ثم انشاء النتائج')
        return HttpResponseRedirect(reverse('result'))
    # Update students on result
    for item in person_in_result:
        get_student = Person.objects.get(pk=item)
        get_result_id = result.get(student_id=get_student)
        get_theoretical_mark = Exam.objects.filter(
            student_id=get_student, session_id=get_result_id.session_id, type_id='نظري').aggregate(Max('mark'))['mark__max']
        get_practical_mark = Exam.objects.filter(
            student_id=get_student, session_id=get_result_id.session_id, type_id='عملي').aggregate(Max('mark'))['mark__max']
        get_attendance = Attendance.objects.filter(
            person_id=get_student, session_id=get_result_id.session_id, status=True).count()
        get_result = (get_theoretical_mark + get_practical_mark) / 2
        get_result_type = 'إعادة'
        if get_practical_mark >= 80:
            if get_theoretical_mark >= 80:
                get_result_type = 'ناجح'
            if get_theoretical_mark < 80:
                if get_theoretical_mark >= 70:
                    get_result_type = 'نجاح شرطي'
        # Edit result
        get_result_id.attendance = get_attendance
        get_result_id.theoretical_mark = get_theoretical_mark
        get_result_id.practical_mark = get_practical_mark
        get_result_id.result = get_result
        get_result_id.result_type = get_result_type
        get_result_id.save()
    # Add students to result
    for item in student:
        get_student = Person.objects.get(pk=item)
        get_session_student = session_student.get(student_id=get_student)
        get_theoretical_mark = Exam.objects.filter(
            student_id=get_student, session_id=get_session_student.session_id, type_id='نظري').aggregate(Max('mark'))['mark__max']
        get_practical_mark = Exam.objects.filter(
            student_id=get_student, session_id=get_session_student.session_id, type_id='عملي').aggregate(Max('mark'))['mark__max']
        get_attendance = Attendance.objects.filter(
            person_id=get_student, session_id=get_session_student.session_id, status=True).count()
        get_result = (get_theoretical_mark + get_practical_mark) / 2
        get_result_type = 'إعادة'
        if get_practical_mark >= 80:
            if get_theoretical_mark >= 80:
                get_result_type = 'ناجح'
            if get_theoretical_mark < 80:
                if get_theoretical_mark >= 70:
                    get_result_type = 'نجاح شرطي'

        count_index = Result.objects.all().count()
        if count_index == 0:
            count_index = 1
        else:
            count_index = Result.objects.all().aggregate(
                Max('result_id'))['result_id__max']
            count_index += 1
        # Add result
        Result.objects.create(result_id=count_index,
                              student_id=get_student,
                              session_id=get_session_student.session_id,
                              attendance=get_attendance,
                              theoretical_mark=get_theoretical_mark,
                              practical_mark=get_practical_mark,
                              result=get_result,
                              result_type=get_result_type)
        count_index += 1
    messages.success(request, 'تم الانشاء بنجاح')
    return HttpResponseRedirect(reverse('result'))


@login_required(login_url='login')
def student_pass(request):
    if request.user.is_staff:
        level = Level.objects.all().order_by('level_id')
        level_list = Level.objects.all().order_by(
            'level_id').values_list('level_id', flat=True)
        last_level = Level.objects.all().order_by('level_id').last()
        get_course_id = get_request_session_course_id(request)
        session = Session.objects.all().filter(course_id=get_course_id)
        session_list = session.values_list('session_id', flat=True)
        # Check if student are in result
        result = Result.objects.filter(session_id__in=session_list)
        exam = Exam.objects.filter(session_id__in=session_list)
        person_in_result = result.values_list('student_id', flat=True)
        # Check if any student is not in exam
        result_count = result.count()
        if result_count == 0:
            messages.error(request, 'الرجاء انشاء النتائج اولا')
            return HttpResponseRedirect(reverse('result'))
        for item in person_in_result:
            get_student = Person.objects.get(pk=item)
            get_result_id = result.get(student_id=get_student)
            get_level_id = get_result_id.session_id.level_id.level_id
            # Check result
            if get_result_id.result_type == 'ناجح':
                get_student.priority_id = 'مستمر'
                next_level_id = 0
                index = 0
                if get_level_id == last_level.level_id:
                    get_student.type_id = 'Graduate'
                    get_student.level_id = level.first()
                    get_student.status = True
                    get_student.save()
                else:
                    for loop_level in level_list:
                        if index == 1:
                            next_level_id = loop_level
                            break
                        elif loop_level == get_level_id:
                            index = 1
                    next_level = Level.objects.get(level_id=next_level_id)
                    get_student.level_id = next_level
                    get_student.status = True
                    get_student.save()
            elif get_result_id.result_type == 'نجاح شرطي':
                get_student.priority_id = 'مستمر'
                next_level_id = 0
                index = 0
                if get_level_id == last_level.level_id:
                    get_student.type_id = 'Graduate'
                    get_student.level_id = level.first()
                    get_student.status = True
                    get_student.save()
                else:
                    for loop_level in level_list:
                        if index == 1:
                            next_level_id = loop_level
                            break
                        elif loop_level == get_level_id:
                            index = 1
                    next_level = Level.objects.get(level_id=next_level_id)
                    get_student.level_id = next_level
                    get_student.status = True
                    get_student.save()
            elif get_result_id.result_type == 'إعادة':
                get_theoretical_mark = exam.filter(
                    student_id=get_student, type_id='نظري').aggregate(Max('mark'))['mark__max']
                get_practical_mark = exam.filter(
                    student_id=get_student, type_id='عملي').aggregate(Max('mark'))['mark__max']
                get_attendance = get_result_id.attendance
                if get_practical_mark == 0 and get_theoretical_mark == 0 and get_attendance < 4:
                    get_student.level_id = get_result_id.session_id.level_id
                    get_student.priority_id = 'غير معروف'
                    get_student.status = False
                    get_student.save()
                elif get_practical_mark == 0 and get_theoretical_mark == 0:
                    get_student.level_id = get_result_id.session_id.level_id
                    get_student.priority_id = 'غير معروف'
                    get_student.status = True
                    get_student.save()
                else:
                    get_student.level_id = get_result_id.session_id.level_id
                    get_student.priority_id = 'مستمر'
                    get_student.status = True
                    get_student.save()
        messages.success(request, 'تم الترحيل بنجاح')
        return HttpResponseRedirect(reverse('result'))
    messages.warning(request, 'ليس لديك صلاحية للقيام بهذه العملية')
    return redirect('result')


def set_result_type(request):
    result_id = request.GET.get('result_id')
    result_type = request.GET.get('result_type')
    if Result.objects.filter(pk=result_id).exists():
        get_result = Result.objects.get(pk=result_id)
        get_result.result_type = result_type
        get_result.save()
    print(result_id)
    print(result_type)
    context = {}
    return JsonResponse(context)


def export_result_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="result.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Results')
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['id', 'First name', 'Last name', 'Course', 'Level',
               'Session', 'Attendance', 'Theoretical', 'Practical', 'Average', 'Result']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    rows = []
    get_course_id = get_request_session_course_id(request)
    in_session = Session.objects.filter(
        course_id=get_course_id).values_list('session_id', flat=True)
    result = Result.objects.filter(session_id__in=in_session)
    for l_result in result:
        id = str(l_result.student_id.person_id)
        fname = str(l_result.student_id.first_name)
        lname = str(l_result.student_id.last_name)
        course = str(l_result.session_id.course_id)
        level = str(l_result.session_id.level_id)
        session = str(l_result.session_id)
        attendance = str(l_result.attendance)
        theoretical = str(l_result.theoretical_mark)
        practical = str(l_result.practical_mark)
        avrage = str(l_result.result)
        result = str(l_result.result_type)
        vlues = [id, fname, lname, course, level, session,
                 attendance, theoretical, practical, avrage, result]
        rows.append(vlues)
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response
