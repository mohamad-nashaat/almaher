from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate ,login, logout
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
from level.models import Level


@login_required(login_url='login')
def level(request):
    level = Level.objects.all().order_by('level_id')
    context = {'level': level,
                }
    return render(request, 'level/level.html', context)

@login_required(login_url='login')
def add_level(request):
    if request.method == 'POST':
        count_index = Level.objects.all().count()
        if count_index == 0:
            count_index = 1
        else:
            count_index = Level.objects.all().aggregate(Max('level_id'))['level_id__max']
            count_index += 1
        nlevel = request.POST['level_name']
        Level.objects.create(level_id=count_index,
                            level_name = nlevel)
        messages.success(request, 'تم الاضافة بنجاح')
        return HttpResponseRedirect(reverse('level'))
    context = {}
    return render(request, 'level/add_level.html', context)

# @login_required(login_url='login')
# def del_level(request, pk):
#     if request.user.is_staff:
#         get_level = Level.objects.get(pk=pk)
#         get_level.delete()
#         messages.success(request, 'تم الحذف بنجاح')
#         return redirect('level')
#     messages.warning(request, 'ليس لديك صلاحية للقيام بهذه العملية')
#     return redirect('level')