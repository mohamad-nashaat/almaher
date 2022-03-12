from django.urls import path
from . import views

urlpatterns = [
    path('select', views.select_attendance, name='attendance'),
    path('teacher', views.attendance_teacher, name='attendance_teacher'),
    path('student', views.attendance_student, name='attendance_student'),
    path('generater', views.attendance_generater, name='attendance_generater'),

    path('change_status_true', views.change_status_true, name='change_status_true'),
    path('change_status_false', views.change_status_false, name='change_status_false'),

    path('export/excel/attendance', views.export_excel_attendance, name='export_excel_attendance'),
    path('export/pdf/attendance/student', views.export_attendance_student_pdf, name='export_attendance_student_pdf'),
    path('export/pdf/attendance/teacher', views.export_attendance_teacher_pdf, name='export_attendance_teacher_pdf'),

]