from django.contrib import admin
from django.urls import include, path

import account

urlpatterns = [
    path('', include('home.urls')),
    path('', include('account.urls')),
    path('admin/', admin.site.urls),
    path('dashboard/course/', include('course.urls')),
    path('dashboard/level/', include('level.urls')),
    path('dashboard/position/', include('position.urls')),
    path('dashboard/period/', include('period.urls')),
    path('dashboard/attendance/', include('attendance.urls')),
    path('dashboard/exam/', include('exam.urls')),
    path('dashboard/person/', include('person.urls')),
    path('dashboard/result/', include('result.urls')),
    path('dashboard/session/', include('session.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
]
