#coding:utf-8 
import csv
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

@transaction.atomic
def upld(request): 
    x = y = 0
    if (request.method == "POST") and ('upload_order' in request.POST):
        uf = UserForm(request.POST, request.FILES)
        if uf.is_valid():
            #handle_uploaded_file(request.FILES['file'])         			
            # 打开文件
            #f = request.FILES['file']
            fname = request.FILES['file'].temporary_file_path()
            #myfile = csv.reader(open(fname, 'r')) 
            
            with open(fname, 'r') as f:
                reader = csv.reader(f)
                
                #print u"读取文件结束,开始导入!"
                time1 = time.time()

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
           
        
            #print "读取文件耗时"+str(time2-time1)+"秒,导入数据耗时"+str(time3-time2)+"秒!"
            time2    = time.time()
            #update_or_create           
            AliOrd.objects.bulk_create(WorkList)
            time3 = time.time()
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
        with open(fname, 'r') as f:
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
        with open(fname, 'r') as f:
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
        with open(fname, 'r') as f:
            reader = csv.reader(f)

            line_num = 0
            for line in reader:
                line_num = line_num + 1
                if (line_num != 1):
                    # add agent entry 机器人广告位
                    if line[1] != '':
                        Agent.objects.update_or_create(AgentId=line[1], AgentName=line[0],
                                                       defaults={'AgentName': line[0]})
                    # add agent entry 小布丁广告位
                    if line[3] != '':
                        Agent.objects.update_or_create(AgentId=line[3], AgentName=line[2],
                                                       defaults={'AgentName': line[2]})
                    # add agent entry APP广告位
                    if line[5] != '':
                        Agent.objects.update_or_create(AgentId=line[5], AgentName=line[4],
                                                       defaults={'AgentName': line[4]})

        # add aliconfig entry
        fname = request.FILES['file'].temporary_file_path()
        with open(fname, 'r') as f:
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

                        # get object
                        if line[1] != '':
                            obj_AgentId = Agent.objects.get(AgentId=line[1])

                        if line[7] != '':
                            obj_AgentUpId = Agent.objects.get(AgentId=line[7])

                        if line[3] != '':
                            obj_ZhaohuoPid = Agent.objects.get(AgentId=line[3])

                        if line[5] != '':
                            obj_AppPid = Agent.objects.get(AgentId=line[5])

                    except ObjectDoesNotExist:
                        ls_error.append(line[0])

                    WorkList.append(AliConfig(AgentId=obj_AgentId,
                                              AgentUpId=obj_AgentUpId,
                                              ZhaohuoPid=obj_ZhaohuoPid,
                                              AppPid=obj_AppPid,
                                              AgentPerc=line[8],
                                              Agent2rdPerc=line[9],
                                              Agent3rdPerc=line[10],
                                              Slug=line[1],
                                              GroupId=group_id))
                    ls_count_succ = ls_count_succ + 1
        AliConfig.objects.bulk_create(WorkList)

        return HttpResponse('成功更新')





