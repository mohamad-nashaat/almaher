from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('blank', views.blank, name='blank'),
    path('404', views.pg_404, name='404'),
]
