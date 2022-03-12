from django.urls import path
from . import views

urlpatterns = [
    path('', views.exam, name='exam'),
    path('generate', views.generate_exam, name='generate_exam'),
    path('set_exam_mark', views.set_exam_mark, name='set_exam_mark'),
    path('export_exam_excel', views.export_exam_excel, name='export_exam_excel'),
]