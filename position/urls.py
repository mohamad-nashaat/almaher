from django.urls import path
from . import views

urlpatterns = [
    path('', views.position, name='position'),
    path('add', views.add_position, name='add_position'),
    # path('del/<str:pk>', views.del_position, name='del_position'),
]
