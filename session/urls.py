from django.urls import path
from . import views

urlpatterns = [
    path('', views.session, name='session'),
    path('generate', views.generate_session, name='generate_session'),
    path('add', views.add_session, name='add_session'),
    path('edit/<int:pk>', views.edit_session, name='edit_session'),
    path('del/<int:pk>', views.del_session, name='del_session'),

    path('student', views.get_session_student,
         name='get_session_student'),
    path('student/<int:pk>', views.session_student, name='session_student'),
    path('student/add/<int:pk>/<int:num>',
         views.add_session_student, name='add_session_student'),
    path('student/del/<int:pk>/<int:num>',
         views.del_session_student, name='del_session_student'),
    path('view', views.view_session_student, name='view_session_student'),
    path('wait_list', views.wait_list_session, name='wait_list_session'),
    path('set_teacher', views.set_teacher, name='set_teacher'),
    path('set_student', views.set_student, name='set_student'),

    path('export/pdf/session/student', views.export_students_session_pdf,
         name='export_students_session_pdf'),
    path('export/pdf/session/teacher', views.export_teacher_session_pdf,
         name='export_teacher_session_pdf'),
    path('export/pdf/session/teacher/student', views.export_teacher_student_session_pdf,
         name='export_teacher_student_session_pdf'),
    path('export/excel/sessions', views.export_sessions_excel,
         name='export_sessions_excel'),

]
