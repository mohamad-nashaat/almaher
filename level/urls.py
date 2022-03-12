from django.urls import path
from . import views

urlpatterns = [
    path('', views.level, name='level'),
    path('add', views.add_level, name='add_level'),
    path('del/<str:pk>', views.del_level, name='del_level'),
]