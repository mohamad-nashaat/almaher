from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.db.models import Q, Max, Prefetch
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
def exam(request):
    get_course_id = get_request_session_course_id(request)
    in_session = Session.objects.filter(
        course_id=get_course_id).values_list('session_id', flat=True)
    get_exam = Exam.objects.filter(session_id__in=in_session)
    student_exam = get_exam.values_list('student_id', flat=True).distinct()
    last_exam = []
    exams = Person.objects.filter(
        pk__in=student_exam).prefetch_related(Prefetch('exam_set', queryset=Exam.objects.filter(session_id__in=in_session).order_by('exam_id').select_related(
            'session_id', 'student_id', 'session_id__level_id')))
    for exam in exams:
        all_exam = exam.exam_set.all()
        dic_exam = {'student_name': all_exam[0].student_id, 'student_id': all_exam[0].student_id.person_id,
                    'session_id': all_exam[0].session_id, 'exams': all_exam}
        last_exam.append(dic_exam)
    context = {'exam': last_exam,
               'get_course_id': get_course_id,
               }
    return render(request, 'exam/exam.html', context)


@login_required(login_url='login')
def generate_exam(request):
    get_course_id = get_request_session_course_id(request)
    # get all students on session in this course and generate 3 type_time and 2 type_exam for each students
    session = Session.objects.all().filter(course_id=get_course_id)
    session_list = session.values_list('session_id', flat=True)
    # Check if student are in exam
    person_in_exam = Exam.objects.filter(
        session_id__in=session_list).values_list('student_id', flat=True)
    session_student = Session_Student.objects.all().filter(session_id__in=session_list)
    student = session_student.filter(
        ~Q(student_id__in=person_in_exam)).values_list('student_id', flat=True)
    # Add student to attendance
    for item in student:
        get_student = Person.objects.get(pk=item)
        get_session_student = session_student.get(student_id=get_student)
        count_index = Exam.objects.all().count()
        if count_index == 0:
            count_index = 1
        else:
            count_index = Exam.objects.all().aggregate(
                Max('exam_id'))['exam_id__max']
            count_index += 1
        # Add 3 Theoretical
        Exam.objects.create(exam_id=count_index, type_id='نظري', time_id='الامتحان الأول',
                            student_id=get_student, session_id=get_session_student.session_id, mark=0)
        count_index += 1
        Exam.objects.create(exam_id=count_index, type_id='نظري', time_id='التكميلي',
                            student_id=get_student, session_id=get_session_student.session_id, mark=0)
        count_index += 1
        Exam.objects.create(exam_id=count_index, type_id='نظري', time_id='الاعادة',
                            student_id=get_student, session_id=get_session_student.session_id, mark=0)
        count_index += 1
        # Add 3 Practical
        Exam.objects.create(exam_id=count_index, type_id='عملي', time_id='الامتحان الأول',
                            student_id=get_student, session_id=get_session_student.session_id, mark=0)
        count_index += 1
        Exam.objects.create(exam_id=count_index, type_id='عملي', time_id='التكميلي',
                            student_id=get_student, session_id=get_session_student.session_id, mark=0)
        count_index += 1
        Exam.objects.create(exam_id=count_index, type_id='عملي', time_id='الاعادة',
                            student_id=get_student, session_id=get_session_student.session_id, mark=0)
        count_index += 1
    messages.success(request, 'تم الانشاء بنجاح')
    return HttpResponseRedirect(reverse('exam'))


def set_exam_mark(request):
    exam_id = request.GET.get('exam_id')
    exam_value = request.GET.get('exam_value')
    exam = Exam.objects.get(pk=exam_id)
    exam.mark = exam_value
    exam.save()
    context = {}
    return JsonResponse(context)


def export_exam_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="exam.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Exam')
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['id', 'First name', 'Last name', 'Course', 'Level',
               'Session',
               'نظري الامتحان الأول', 'نظري الإعادة', 'نظري التكميلي',
               'عملي الامتحان الأول', 'عملي الإعادة', 'عملي التكميلي'
               ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    rows = []
    get_course_id = get_request_session_course_id(request)
    in_session = Session.objects.filter(
        course_id=get_course_id).values_list('session_id', flat=True)
    get_exam = Exam.objects.filter(session_id__in=in_session)
    student_exam = get_exam.values_list('student_id', flat=True).distinct()
    exam = []
    for all_person in student_exam:
        first_exam = get_exam.filter(student_id=all_person).first()
        all_exam = get_exam.filter(student_id=all_person).values_list(
            'mark', flat=True).order_by('exam_id')
        dic_exam = {'student_id': first_exam.student_id,
                    'session_id': first_exam.session_id, 'exams': all_exam}
        exam.append(dic_exam)
    print(exam)
    for l_exam in exam:
        id = str(l_exam['student_id'].person_id)
        fname = str(l_exam['student_id'].first_name)
        lname = str(l_exam['student_id'].last_name)
        course = str(l_exam['session_id'].course_id)
        level = str(l_exam['session_id'].level_id)
        session = str(l_exam['session_id'].session_number)
        vlues = [id, fname, lname, course, level, session]
        for mark in l_exam['exams']:
            vlues.append(str(mark))
        rows.append(vlues)
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response
