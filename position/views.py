from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.db.models import Max
from django.db.models import Q
import xlwt
import tempfile
from django.template.loader import render_to_string
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration
# Import models
from position.models import Position


@login_required(login_url='login')
def position(request):
    position = Position.objects.all()
    context = {'position': position,
               }
    return render(request, 'position/position.html', context)


@login_required(login_url='login')
def add_position(request):
    if request.method == 'POST':
        nposition = request.POST['position_name']
        Position.objects.create(position_name=nposition)
        messages.success(request, 'تم الاضافة بنجاح')
        return HttpResponseRedirect(reverse('position'))
    context = {}
    return render(request, 'position/add_position.html', context)

# @login_required(login_url='login')
# def del_position(request, pk):
#     if request.user.is_staff:
#         get_position = Position.objects.get(pk=pk)
#         get_position.delete()
#         messages.success(request, 'تم الحذف بنجاح')
#         return redirect('position')
#     messages.warning(request, 'ليس لديك صلاحية للقيام بهذه العملية')
#     return redirect('position')
