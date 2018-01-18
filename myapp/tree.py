# coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse

from myapp.models import AliConfig, AliOrd, PayResult

def tree(request):
    current_year = '2017'
    current_month = '12'
    agent_list = PayResult.objects.filter(CalculateYear=current_year, CalculateMonth=current_month)

    return render(request, "myapp/tree.html", {'agent_list': agent_list})
