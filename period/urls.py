from django.urls import path
from . import views

urlpatterns = [
    path('', views.period, name='period'),
    path('add', views.add_period, name='add_period'),
    path('del/<str:pk>', views.del_period, name='del_period'),
]