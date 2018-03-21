# coding:utf-8
# -*- coding: UTF-8 -*-
import csv
import xlwt

#import os 
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "www.settings") 

#import django

# if django.VERSION >= (1, 7):#自动判断版本222
    # django.setup()

#from arrears.models import D072Qf 
from myapp.models import AliOrd, Agent, AliConfig, PayResult
from django.shortcuts import render,render_to_response
from django import forms
from django.http import HttpResponse
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

import time
import random
from django.http.multipartparser import FILE
from builtins import int

class UserForm(forms.Form):
    #title = forms.CharField(max_length=50)
    file = forms.FileField()

def upld(request):
    x = y = 0
    if (request.method == "POST") and ('upload_order' in request.POST):
        uf = UserForm(request.POST, request.FILES)
        if uf.is_valid():
            #handle_uploaded_file(request.FILES['file'])         			
            # 打开文件
            #f = request.FILES['file']
            fname = request.FILES['file'].temporary_file_path()
            #myfile = csv.reader(open(fname, 'r', encoding="utf-8"))
            
            with open(fname, 'r', encoding="utf-8") as f:
                reader = csv.reader(f)
                
                WorkList = []
                line_num = 0
                x = y = 0
                for line in reader: 
                    line_num = line_num + 1
                    if (line_num != 1): 
                        if AliOrd.objects.filter(OrderId=line[24]).exists():
                            x = x + 1
                            AliOrd.objects.filter(OrderId=line[24]).delete()
                        else:
                            y = y + 1
                            WorkList.append(AliOrd(CreatDate=line[0],
                                               ClickDate=line[1],
                                               CommType=line[2],
                                               CommId=line[3],
                                               WangWangId=line[4],
                                               StoreId=line[5],
                                               CommQty=line[6],
                                               CommPrice=line[7],
                                               OrdStatus=line[8],
                                               OrdType=line[9],
                                               IncomePerc=line[10],
                                               DividePerc=line[11],
                                               PayAmount=line[12],
                                               EstAmount=line[13],
                                               SettleAmt=line[14],
                                               EstIncome=line[15],
                                               SettleDate=line[16],
                                               RebatePerc=line[17],
                                               RebateAmt=line[18],
                                               AllowancePerc=line[19],
                                               AllowanceAmt=line[20],
                                               AllowanceType=line[21],
                                               Platform=line[22],
                                               ThirdParty=line[23],
                                               OrderId=int(line[24]),
                                               Category=line[25],
                                               MediaId=line[26],
                                               MediaName=line[27],
                                               PosID=line[28],
                                               PosName=line[29]))
           
            #update_or_create
            AliOrd.objects.bulk_create(WorkList)
            order_list = []
            agent_file = UserForm()
            								
            #return HttpResponse('upload ok!')
        
    elif (request.method == "POST") and ('upload_agent' in request.POST):
        upload_agent_group(request)
        return HttpResponse('upload ok!')
    
    elif (request.method == "POST") and ('delete_order' in request.POST):   
            
        AliOrd.objects.all().delete()
        # PayResult.objects.all().delete()
        #return HttpResponse('所有订单已删除')
        return render(request, 'myapp/upld.html', {'context': '所有订单已删除'})

    elif (request.method == "POST") and ('download_all_agent' in request.POST):
        agent_list = AliConfig.objects.all()

        wb = xlwt.Workbook()

        ws = wb.add_sheet('所有代理信息')
        style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',
                             num_format_str='#,##0.00')
        line_0 = [u'淘宝订单号', u'订单创建时间', u'订单结算时间', u'商品信息', u'商品类目', u'商品数量', u'商品单价',
                  u'订单状态', u'订单类型', u'付款金额', u'代理ID', u'代理', u'代理上线ID', u'代理上线', u'佣金金额']
        # 生成第一行
        for i in range(0, len(line_0)):
            ws.write(0, i, line_0[i], style0)
        line_num = 1
        for agent in agent_list:
            ws.write(line_num, 0, str(agent.AgentId))
            ws.write(line_num, 12, str(agent.AgentPerc))

            line_num = line_num + 1

        response = HttpResponse(content_type='application/msexcel')
        response['Content-Disposition'] = 'attachment; filename=agents.csv'
        wb.save(response)
        return response

    else:
        uf = UserForm()
        agent_file = UserForm()
        #Person.objects.filter(age__gt=18).values_list()#括号可以指定需要的字段，一般使用这种方法。
        order_list = AliOrd.objects.all()
    return render(request, 'myapp/upld.html', {'uf':uf,
                                         'upd_unm':x,
                                         'new_unm':y,
                                         'order_list':order_list,
                                         'agent_file':agent_file})

def UploadAgent(request):
    agent_file = UserForm(request.POST, request.FILES)
    
    if agent_file.is_valid():
        # 打开文件
        # add agent entry
        fname = request.FILES['file'].temporary_file_path()
        with open(fname, 'r', encoding="utf-8") as f:
            reader = csv.reader(f)
            
            line_num = 0
            for line in reader: 
                line_num = line_num + 1
                if (line_num != 1): 
                    # add agent entry
                    # Agent.objects.get_or_create(AgentId  = line[0],
                    #                             AgentName= line[1])
                    Agent.objects.update_or_create(AgentId  = line[0], AgentName= line[1],
                                                    defaults={'AgentName': line[1]})



        # add aliconfig entry            
        fname = request.FILES['file'].temporary_file_path()
        with open(fname, 'r', encoding="utf-8") as f:
            reader = csv.reader(f)                    
            
            WorkList = []
            ls_error= []
            ls_count_succ = 0
                    
            line_num = 0
            for line in reader: 
                line_num = line_num + 1
                
                if (line_num != 1):   # skip the first line
                    try:
                        obj_AgentId   = None
                        obj_AgentUpId = None
                        #get object 
                        obj_AgentId = Agent.objects.get(AgentId=line[0])
                        obj_AgentUpId = Agent.objects.get(AgentId=line[5])
                    except ObjectDoesNotExist:
                        ls_error.append(line[0])
                            
                    if not obj_AgentId == None:                                                        
                        WorkList.append(AliConfig(AgentId=obj_AgentId,
                                        AgentUpId=obj_AgentUpId,
                                        AgentPerc = line[6],
                                        Agent2rdPerc = line[7],
                                        Agent3rdPerc = line[8],
                                        Slug = line[0]))
                        ls_count_succ = ls_count_succ + 1
        AliConfig.objects.bulk_create(WorkList)                                           
                                                               
#                    AliConfig.objects.get_or_create(AgentId   = obj_AgentId,
#                                                    AgentUpId = obj_AgentUpId)
#                                                        AgentPerc = line[6],
#                                                        Agent2rdPerc = line[7],
#                                                        Agent3rdPerc = line[8])                 
        return HttpResponse('成功更新')


def upload_agent_group(request):
    agent_file = UserForm(request.POST, request.FILES)

    if agent_file.is_valid():
        # 打开文件
        # add agent entry
        fname = request.FILES['file'].temporary_file_path()
        with open(fname, 'r', encoding="utf-8") as f:
            reader = csv.reader(f)

            line_num = 0
            for line in reader:
                line_num = line_num + 1
                if (line_num != 1):
                    # add agent entry 机器人广告位
                    if line[2] != '':
                        Agent.objects.update_or_create(AgentId=line[2],
                                                       defaults={'AgentName': line[1]})
                    # add agent entry 小布丁广告位
                    if line[4] != '':
                        Agent.objects.update_or_create(AgentId=line[4],
                                                       defaults={'AgentName': line[3]})
                    # add agent entry APP广告位
                    if line[6] != '':
                        Agent.objects.update_or_create(AgentId=line[6],
                                                       defaults={'AgentName': line[5]})
                    # add agent entry 京东广告位
                    if line[8] != '':
                        Agent.objects.update_or_create(AgentId=line[8],
                                                       defaults={'AgentName': line[7]})
        # add aliconfig entry
        fname = request.FILES['file'].temporary_file_path()
        with open(fname, 'r', encoding="utf-8") as f:
            reader = csv.reader(f)

            WorkList = []
            ls_error = []
            ls_count_succ = 0

            line_num = 0
            group_id = 0
            for line in reader:
                line_num = line_num + 1

                if (line_num != 1):  # skip the first line
                    try:
                        group_id = group_id + 1
                        obj_AgentId = None
                        obj_AgentUpId = None
                        obj_ZhaohuoPid = None
                        obj_AppPid = None
                        obj_JDPid = None

                        # get object
                        if line[2] != '':
                            obj_AgentId = Agent.objects.get(AgentId=line[2])

                        if line[10] != '':
                            obj_AgentUpId = Agent.objects.get(AgentId=line[10])

                        if line[4] != '':
                            obj_ZhaohuoPid = Agent.objects.get(AgentId=line[4])

                        if line[6] != '':
                            obj_AppPid = Agent.objects.get(AgentId=line[6])

                        if line[8] !='':
                            obj_JDPid = Agent.objects.get(AgentId=line[8])

                    except ObjectDoesNotExist:
                        ls_error.append(line[0])

                    WorkList.append(AliConfig(AgentName=line[0],
                                              AgentId=obj_AgentId,
                                              AgentUpId=obj_AgentUpId,
                                              ZhaohuoPid=obj_ZhaohuoPid,
                                              AppPid=obj_AppPid,
                                              JDPid=obj_JDPid,
                                              AgentPerc=line[11],
                                              Agent2rdPerc=line[12],
                                              Agent3rdPerc=line[13],
                                              Slug=line[2],
                                              GroupId=group_id))
                    ls_count_succ = ls_count_succ + 1
        AliConfig.objects.bulk_create(WorkList)

        return HttpResponse('成功更新')





