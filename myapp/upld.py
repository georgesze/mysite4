# coding:utf-8
# -*- coding: UTF-8 -*-
import csv
import xlwt

# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "www.settings")

# import django

# if django.VERSION >= (1, 7):#自动判断版本222
# django.setup()

# from arrears.models import D072Qf
from myapp.models import AliOrd, Agent, AliConfig, PayResult
from django.shortcuts import render, render_to_response
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
    # title = forms.CharField(max_length=50)
    file = forms.FileField()


def upld(request):
    x = y = 0
    if (request.method == "POST") and ('upload_order' in request.POST):
        uf = UserForm(request.POST, request.FILES)
        if uf.is_valid():
            # handle_uploaded_file(request.FILES['file'])
            # 打开文件
            # f = request.FILES['file']
            fname = request.FILES['file'].temporary_file_path()
            # myfile = csv.reader(open(fname, 'r', encoding='UTF-8'))

            with open(fname, 'r', encoding='UTF-8') as f:
                reader = csv.reader(f)

                WorkList = []
                line_num = 0
                x = y = 0
                for line in reader:
                    line_num = line_num + 1
                    if (line_num != 1):
                        # if AliOrd.objects.filter(OrderId=line[24]).exists():
                        #     x = x + 1
                        #     AliOrd.objects.filter(OrderId=line[24]).delete()
                        # else:
                        #     y = y + 1
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

            # update_or_create
            AliOrd.objects.bulk_create(WorkList)
            order_list = []
            agent_file = UserForm()

            # return HttpResponse('upload ok!')

    elif (request.method == "POST") and ('upload_agent' in request.POST):
        upload_agent(request)
        #upload_agent_group(request)
        return HttpResponse('upload ok!')

    elif (request.method == "POST") and ('delete_order' in request.POST):

        AliOrd.objects.all().delete()
        # PayResult.objects.all().delete()
        # return HttpResponse('所有订单已删除')
        return render(request, 'myapp/upld.html', {'context': '所有订单已删除'})

    elif (request.method == "POST") and ('download_all_agent' in request.POST):
        agent_list = AliConfig.objects.all()

        wb = xlwt.Workbook()

        ws = wb.add_sheet('所有代理信息')
        style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',
                             num_format_str='#,##0.00')
        line_0 = [u'合伙人ID', u'代理机器人名称', u'代理机器人ID', u'代理找货名称', u'代理找货ID', u'代理APP名称', u'代理APPID',
                  u'代理京东名称', u'京东ID', u'代理上线', u'上线机器人ID', u'自获佣金比例', u'提取二级佣金比例', u'提取三级佣金比例', u'加入时间', u'已删除合伙人',
                  u'支付姓名', u'支付账户']
        # 生成第一行
        for i in range(0, len(line_0)):
            ws.write(0, i, line_0[i], style0)
        line_num = 1
        for agent in agent_list:
            ws.write(line_num, 0, str(agent.GroupId))
            ws.write(line_num, 1, str(agent.AgentName))
            ws.write(line_num, 2, str(agent.AgentId))
            ws.write(line_num, 3, str(agent.ZhaohuoPid.AgentName if agent.ZhaohuoPid else ""))
            ws.write(line_num, 4, str(agent.ZhaohuoPid))
            ws.write(line_num, 5, str(agent.AppPid.AgentName if agent.AppPid else ""))
            ws.write(line_num, 6, str(agent.AppPid))
            ws.write(line_num, 7, str(agent.JDPid.AgentName if agent.JDPid else ""))
            ws.write(line_num, 8, str(agent.JDPid))
            ws.write(line_num, 9, str(agent.AgentUpId.AgentName if agent.AgentUpId else ""))
            ws.write(line_num, 10, str(agent.AgentUpId))
            ws.write(line_num, 11, str(agent.AgentPerc))
            ws.write(line_num, 12, str(agent.Agent2rdPerc))
            ws.write(line_num, 13, str(agent.Agent3rdPerc))
            ws.write(line_num, 14, str(agent.ValidBegin))
            ws.write(line_num, 15, str(agent.Active))
            ws.write(line_num, 16, str(agent.PayName))
            ws.write(line_num, 17, str(agent.PayAccount))

            line_num = line_num + 1

        response = HttpResponse(content_type='application/msexcel')
        response['Content-Disposition'] = 'attachment; filename=agents.csv'
        wb.save(response)
        return response

    else:
        uf = UserForm()
        agent_file = UserForm()
        # Person.objects.filter(age__gt=18).values_list()#括号可以指定需要的字段，一般使用这种方法。
        order_list = AliOrd.objects.all()
    return render(request, 'myapp/upld.html', {'uf': uf,
                                               'upd_unm': x,
                                               'new_unm': y,
                                               'order_list': order_list,
                                               'agent_file': agent_file})


def upload_agent(request):
    agent_file = UserForm(request.POST, request.FILES)
    response_return = ' '
    if agent_file.is_valid():
        # 打开文件
        # add agent entry
        fname = request.FILES['file'].temporary_file_path()
        with open(fname, 'r') as f:
            #, encoding='UTF-8'
            reader = csv.reader(f)

            line_num = 0
            for line in reader:
                line_num = line_num + 1
                if line_num == 1:
                    pass
                if line_num != 1:
                    # add agent entry 机器人广告位
                    if line[2] != '':
                        Agent.objects.update_or_create(AgentId=line[2],
                                                       defaults={'AgentName': line[1]})
                    # add agent entry 上线广告位
                    if line[10] != '':
                        agent_up_id = Agent.objects.update_or_create(AgentId=line[10],
                                                                     defaults={'AgentName': line[9]})

                    # add agent entry 小布丁找货广告位
                    if line[4] != '':
                        zhaohuo_pid = Agent.objects.update_or_create(AgentId=line[4],
                                                                     defaults={'AgentName': line[3]})
                    # add agent entry APP广告位
                    if line[6] != '':
                        app_pid = Agent.objects.update_or_create(AgentId=line[6],
                                                                 defaults={'AgentName': line[5]})
                    # add agent entry 京东广告位
                    if line[8] != '':
                        jd_pid = Agent.objects.update_or_create(AgentId=line[8],
                                                                defaults={'AgentName': line[7]})
                    # 更新 aliconfig 表
                    if line[2] != '':
                        AliConfig.objects.update_or_create(AgentId=Agent.objects.get(AgentId=line[2]),
                                                           defaults={'GroupId': line[0],
                                                                     'AgentUpId': agent_up_id[0],
                                                                     'ZhaohuoPid': zhaohuo_pid[0],
                                                                     'AppPid': app_pid[0],
                                                                     'JDPid': jd_pid[0],
                                                                     'AgentName': line[1],
                                                                     'AgentPerc': line[11],
                                                                     'Agent2rdPerc': line[12],
                                                                     'Agent3rdPerc': line[13],
                                                                     'Slug': line[2],
                                                                     'PayName': line[16],
                                                                     'PayAccount': line[17]
                                                                     })
                        response_return = '成功更新'

    return HttpResponse(response_return)




def upload_agent_group(request):
    agent_file = UserForm(request.POST, request.FILES)

    if agent_file.is_valid():
        # 打开文件
        # add agent entry
        fname = request.FILES['file'].temporary_file_path()
        with open(fname, 'r', encoding='UTF-8') as f:
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
        with open(fname, 'r', encoding='UTF-8') as f:
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

                        if line[8] != '':
                            obj_JDPid = Agent.objects.get(AgentId=line[8])

                    except ObjectDoesNotExist:
                        ls_error.append(line[0])

                    WorkList.append(AliConfig(AgentName=line[1],
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
