from django.urls import path
from . import views

urlpatterns = [
    path('', views.person, name='person'),
    path('edit/<int:pk>', views.edit_person, name='edit_person'),
    path('del/<int:pk>', views.del_person, name='del_person'),
    path('lock/<int:pk>', views.lock_person, name='lock_person'),
    path('unlock/<int:pk>', views.unlock_person, name='unlock_person'),
    path('graduate', views.graduate, name='graduate'),
    path('wait_list', views.wait_list, name='wait_list'),
    # Urls Teachers
    path('teacher', views.teacher, name='teacher'),
    path('teacher/add', views.add_teacher, name='add_teacher'),
    # Urls Students
    path('student', views.student, name='student'),
    path('student/add', views.add_student, name='add_student'),
    
    path('set_priority', views.set_priority, name='set_priority'),
    path('export/excel/person', views.export_excel_person, name='export_excel_person'),
    path('export/excel/student', views.export_excel_student, name='export_excel_student'),
    path('export/excel/teacher', views.export_excel_teacher, name='export_excel_teacher'),
    path('export/excel/graduate', views.export_excel_graduate, name='export_excel_graduate'),
]