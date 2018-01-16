#coding:utf-8

from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render


def AliTransfer(request):
    return render(request, 'myapp/transfer.html')
