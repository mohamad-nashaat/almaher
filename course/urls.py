from django.urls import path
from . import views

urlpatterns = [
    path('', views.course, name='course'),
    path('select', views.select_course, name='select_course'),
    path('add', views.add_course, name='add_course'),
    # path('del/<int:pk>', views.del_course, name='del_course'),
]