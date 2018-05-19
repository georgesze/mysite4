# coding:utf-8
from django.core.exceptions import ObjectDoesNotExist
#from django.db.models.fields.related_descriptors import RelatedObjectDoesNotExist

from django.shortcuts import render
from django.views.decorators import csrf
from django.db.models import Count, Min, Sum, Avg
from myapp.models import AliConfig, AliOrd, PayResult
from django import forms
from django.core import serializers
from django.db import transaction
from datetime import datetime
from django.http import HttpResponse
from time import ctime,sleep
from django.db import DatabaseError

import logging
import datetime
import json
import decimal
import xlwt
import threading


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

class SearchForm(forms.Form):
    now = datetime.datetime.now()
    this_month_start = datetime.datetime(now.year, now.month, 1)
    last_month_end = this_month_start - datetime.timedelta(days=1)
    last_month_start = datetime.datetime(last_month_end.year, last_month_end.month, 1)

    period_str = forms.DateField(initial= last_month_start.date(), widget=forms.SelectDateWidget())
    period_end = forms.DateField(initial= last_month_end.date(), widget=forms.SelectDateWidget())

class myThread (threading.Thread):   #继承父类threading.Thread
    def __init__(self,i_mylog, i_agent, i_start, i_end):
        threading.Thread.__init__(self)
        self.i_agent = i_agent
        self.i_start = i_start
        self.i_end = i_end
        self.i_mylog = i_mylog
    def run(self):                   #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        call_thread(self.i_mylog, self.i_agent, self.i_start, self.i_end)

# 接收POST请求数据    payslip 1
def AgentList(request):
    # 拿到所有agent配置
    current_payment = AliConfig.objects.all()
    Incometotal = 0
    collect_sum = 0

    if (request.method == "POST") and ('calculate_income' in request.POST):
        # 计算工资
        if request.method == "POST":
            start = datetime.datetime.strptime(request.POST.get('req_start'), "%Y-%m-%d").date()
            start_str = str(start)
            request.session['start'] = start_str

            end = datetime.datetime.strptime(request.POST.get('req_end'), "%Y-%m-%d").date()
            end_str = str(end)
            request.session['end'] = end_str
            end = end + datetime.timedelta(days=1)

            current_year = start.strftime('%Y')
            current_month = start.strftime('%m')

            # # 取到当前一期代理工资----用于显示
            # current_payment = PayResult.objects.filter(CalculateYear=current_year, CalculateMonth=current_month)

            # 取到所有代理列表----用于计算
            agent_list = AliConfig.objects.all()

            # 取到期间总金额 from upload
            aggregated = AliOrd.objects.filter(SettleDate__range=(start, end)).aggregate(total=Sum('RebateAmt'))
            Incometotal = aggregated['total']

            # 遍历所有 代理 计算
            for agent in agent_list:
                # 计算所有订单佣金 volume 20000+
                CalculateOrderAgent(agent, start, end)

                # 分别计算机器人,找货，APP的订单
                agent_pid = agent.AgentId
                orders = AliOrd.objects.filter(PosID=agent_pid, SettleDate__range=(start, end))
                CalculateOrderAmount(agent, orders)

                #ZhaohuoPid can be None type
                agent_pid = str(agent.ZhaohuoPid)
                orders = AliOrd.objects.filter(PosID=agent_pid, SettleDate__range=(start, end))
                CalculateOrderAmount(agent, orders)

                agent_pid = str(agent.AppPid)
                orders = AliOrd.objects.filter(PosID=agent_pid, SettleDate__range=(start, end))
                CalculateOrderAmount(agent, orders)

            # 遍历所有 代理 计算 2
            for agent in agent_list:
                # 计算收入 个人订单收入 + 一级下线贡献佣金 + 二级下线贡献佣金
                CalculateIncome(agent, start, end)

                # 保存月佣金计算记录
                save_pay_result(agent, start, end)

                # 取到当前一期代理工资----用于显示
                current_payment = PayResult.objects.filter(CalculateYear=current_year, CalculateMonth=current_month)

    elif (request.method == "POST") and ('calculate_income_bg' in request.POST):
        # 后台多线程计算工资
        start = datetime.datetime.strptime(request.POST.get('req_start'), "%Y-%m-%d").date()
        start_str = str(start)
        request.session['start'] = start_str

        end = datetime.datetime.strptime(request.POST.get('req_end'), "%Y-%m-%d").date()
        end_str = str(end)
        request.session['end'] = end_str
        end = end + datetime.timedelta(days=1)

        current_year = start.strftime('%Y')
        current_month = start.strftime('%m')

        # 取到所有代理列表----用于计算
        agent_list = AliConfig.objects.all()
        #AliConfig.objects.all().update(CalculateStatus='IP')

        # 取到期间总金额 from upload
        aggregated = AliOrd.objects.filter(SettleDate__range=(start, end)).aggregate(total=Sum('RebateAmt'))
        Incometotal = aggregated['total']

        # 遍历所有 代理 计算
        threads = []
        mylog = logging.getLogger('mylog.file')
        mylog.warning('开始多线程计算工资')

        for agent in agent_list:
            # check if PayResult exist
            try:
                q_payresult = PayResult.objects.get(AgentId=agent.AgentId, CalculateYear=current_year,
                                                    CalculateMonth=current_month)
            except ObjectDoesNotExist:
                # 创建线程LIST
                t1 = myThread(mylog, agent, start, end)
                threads.append(t1)
            else:
                if q_payresult.CalculateStatus != 'CPL':
                    # 创建线程LIST
                    t1 = myThread(mylog, agent, start, end)
                    threads.append(t1)

        for t in threads:
            # 开启线程
            t.setDaemon(True)
            t.start()

        # 等待主线程终止
        sleep(5)
        t.join()

        for agent in agent_list:
            sumup_pay_result(agent, start, end)
            # 保存月佣金计算记录
            save_sumup_result(agent, start, end)


        # 取到当前一期代理工资----用于显示
        current_payment = PayResult.objects.filter(CalculateYear=current_year, CalculateMonth=current_month)


    elif (request.method == "POST") and ('display_income' in request.POST):
        if request.method == "POST":
            start = datetime.datetime.strptime(request.POST.get('req_start'), "%Y-%m-%d").date()
            start_str = str(start)
            request.session['start'] = start_str

            end = datetime.datetime.strptime(request.POST.get('req_end'), "%Y-%m-%d").date()
            end_str = str(end)
            request.session['end'] = end_str
            end = end + datetime.timedelta(days=1)

            current_year = start.strftime('%Y')
            current_month = start.strftime('%m')

            # 取到当前一期代理工资
            current_payment = PayResult.objects.filter(CalculateYear=current_year, CalculateMonth=current_month)
            aggregated1 = PayResult.objects.filter(CalculateYear=current_year, CalculateMonth=current_month).aggregate(total=Sum('IncomeTotal'))
            Incometotal = aggregated1['total']

            # 取到期间总金额 from upload CSV file
            aggregated2 = AliOrd.objects.filter(SettleDate__range=(start, end)).aggregate(total=Sum('RebateAmt'))
            collect_sum = aggregated2['total']

    else:
        start_str = str(get_date('last_month_start'))
        end_str = str(get_date('last_month_end'))

    return render(request, "myapp/payslip.html", {'form_agent': current_payment,
                                            'req_start': start_str,
                                            'req_end': end_str,
                                            # 'form_period': form,
                                            'Incometotal': Incometotal,
                                            'CollectSum': collect_sum})

def AgentTree(request):
    # 拿到所有agent配置    payslip 2
    agent_list = AliConfig.objects.all()
    Incometotal = 0

    form = SearchForm()

    aggregated = AliConfig.objects.all().aggregate(total=Sum('IncomeTotal'))
    CollectSum = aggregated['total']

    queryset_agent = AliConfig.objects.all()
    all_records_count = queryset_agent.count()

    json_agent = {'total': all_records_count, 'rows': []}

    for agent in queryset_agent:
        json_agent['rows'].append({
            "AgentId": agent.AgentId.AgentId if agent.AgentId else "",
            "AgentName": agent.AgentId.AgentName if agent.AgentId else "",
            "AgentUpId": agent.AgentUpId.AgentId if agent.AgentUpId else "",
            "AgentUpName": agent.AgentUpId.AgentName if agent.AgentUpId else "",
            "AgentPerc": agent.AgentPerc,
            "Agent2rdPerc": agent.Agent2rdPerc,
            "Agent3rdPerc": agent.Agent3rdPerc,
            "IncomeSelf": agent.IncomeSelf,
            "IncomeLv1": agent.IncomeLv1,
            "IncomeLv2": agent.IncomeLv2,
            "IncomeTotal": agent.IncomeTotal,
            "CalculateStatus": agent.CalculateStatus,
            "Slug": '<a href="myapp/payslip/%s">Click me</a>' % agent.Slug,

            #                 <td align="right"><a href="/payslip/{{ AliConfig.Slug }}">点我查看明细</a></td>
        })
    #     json_agent =  serializers.serialize('json', AliConfig.objects.all())

    return_dict = {'json_agent': json.dumps(json_agent, cls=DecimalEncoder),
                   'form_period': form,
                   'Incometotal': Incometotal,
                   'CollectSum': CollectSum}

    return render(request, "myapp/agent_payslip.html", return_dict)


def AgentDetail(request, agent_name_slug):
    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}

    try:
        current_agent = AliConfig.objects.get(Slug=agent_name_slug)
        if current_agent.AgentId is not None:
            context_dict['agent_name'] = current_agent.AgentId.AgentName + current_agent.AgentId.AgentId
        else:
            context_dict['agent_name'] = '临时代理'

        start = request.session.get('start')
        end = request.session.get('end')

        start = datetime.datetime.strptime(start, "%Y-%m-%d").date()
        end = datetime.datetime.strptime(end, "%Y-%m-%d").date()

        # 1.当前代理佣金明细
        # settle date 订单结算时间
        if current_agent.AgentId is not None:
            agent_orders = AliOrd.objects.filter(PosID=current_agent.AgentId, SettleDate__range=(start, end))
            context_dict['agent_orders'] = agent_orders

        if current_agent.ZhaohuoPid is not None:
            agent_orders = AliOrd.objects.filter(PosID=current_agent.ZhaohuoPid, SettleDate__range=(start, end))
            context_dict['agent_orders_zh'] = agent_orders

        if current_agent.AppPid is not None:
            agent_orders = AliOrd.objects.filter(PosID=current_agent.AppPid, SettleDate__range=(start, end))
            context_dict['agent_orders_app'] = agent_orders

        context_dict['current_agent'] = current_agent

        # 2.所有下线佣金明细
        if current_agent.AgentId is not None:
            agent_orders_2 = AliOrd.objects.filter(UplineId=current_agent.AgentId,
                                                   SettleDate__range=(start, end)).order_by('PosID')
            context_dict['agent_orders_2'] = agent_orders_2

        # 3.所有下下线佣金明细
            agent_orders_3 = AliOrd.objects.filter(Up2lineId=current_agent.AgentId,
                                               SettleDate__range=(start, end)).order_by('PosID')
            context_dict['agent_orders_3'] = agent_orders_3

    except AliConfig.DoesNotExist:
        # We get here if we didn't find the specified order.
        # Don't do anything - the template displays the "no order" message for us.
        pass

    if (request.method == "POST") and ('download_statement' in request.POST):
        # style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',
        #                  num_format_str='#,##0.00')
        # style1 = xlwt.easyxf(num_format_str='#')

        wb = xlwt.Workbook()

        if 'agent_orders' in context_dict:
            ws = wb.add_sheet('当前代理机器人佣金' + context_dict['agent_name'])
            excel_add_sheet(ws, context_dict['agent_orders'])

        if 'agent_orders_app' in context_dict:
            ws = wb.add_sheet('当前代理app佣金' + context_dict['agent_name'])
            excel_add_sheet(ws, context_dict['agent_orders_app'])

        if 'agent_orders_zh' in context_dict:
            ws = wb.add_sheet('当前代理找货佣金' + context_dict['agent_name'])
            excel_add_sheet(ws, context_dict['agent_orders_zh'])

        if 'agent_orders_2' in context_dict:
            ws = wb.add_sheet('所有一级下线订单')
            excel_add_sheet(ws, context_dict['agent_orders_2'])

        if 'agent_orders_3' in context_dict:
            ws = wb.add_sheet('所有二级下线订单')
            excel_add_sheet(ws, context_dict['agent_orders_3'])

        response = HttpResponse(content_type='application/msexcel')
        response['Content-Disposition'] = 'attachment; filename=example.xls'
        wb.save(response)
        return response

        # Go render the response and return it to the client.
    return render(request, 'myapp/order.html', context_dict)


def CalculateOrderAgent(agent, start, end):
    agent_pid = str(agent.AgentId)
    zhaohuo_pid = str(agent.ZhaohuoPid)
    app_pid = str(agent.AppPid)

    l_UplineId = None
    l_UplineName = None
    l_Up2lineId = None
    l_Up2lineName = None

    if agent.AgentUpId is not None:
        l_UplineId = str(agent.AgentUpId)  # 上线ID
        l_UplineName = str(agent.AgentUpId.AgentName)  # 上线名称

        if agent.AgentUpId.AId is not None: # AI反向链接 AgentId one on one 字段
            l_Up2lineId = str(agent.AgentUpId.AId.AgentUpId)  # 上上线ID

            if agent.AgentUpId.AId.AgentUpId is not None:
                l_Up2lineName = str(agent.AgentUpId.AId.AgentUpId.AgentName)  # 上上线名称
            else:
                pass

    # 机器人 PID
    AliOrd.objects.filter(PosID=agent_pid, SettleDate__range=(start, end)).update(UplineId=l_UplineId,
                                                                                  UplineName=l_UplineName,
                                                                                  Up2lineId=l_Up2lineId,
                                                                                  Up2lineName=l_Up2lineName,
                                                                                  IncomePercSelf=agent.AgentPerc,
                                                                                  SharePercUp1=agent.Agent2rdPerc,
                                                                                  SharePercUp2=agent.Agent3rdPerc)
    # 找货PID
    AliOrd.objects.filter(PosID=zhaohuo_pid, SettleDate__range=(start, end)).update(UplineId=l_UplineId,
                                                                                  UplineName=l_UplineName,
                                                                                  Up2lineId=l_Up2lineId,
                                                                                  Up2lineName=l_Up2lineName,
                                                                                  IncomePercSelf=agent.AgentPerc,
                                                                                  SharePercUp1=agent.Agent2rdPerc,
                                                                                  SharePercUp2=agent.Agent3rdPerc)
    # APP ID
    AliOrd.objects.filter(PosID=app_pid, SettleDate__range=(start, end)).update(UplineId=l_UplineId,
                                                                                  UplineName=l_UplineName,
                                                                                  Up2lineId=l_Up2lineId,
                                                                                  Up2lineName=l_Up2lineName,
                                                                                  IncomePercSelf=agent.AgentPerc,
                                                                                  SharePercUp1=agent.Agent2rdPerc,
                                                                                  SharePercUp2=agent.Agent3rdPerc)

def CalculateOrderAmount(agent, orders):
    for order_item in orders:
        update_flag = False

        l_temp = round(order_item.RebateAmt * agent.AgentPerc, 2)
        if not order_item.IncomeSelf == l_temp:
            update_flag = True
            order_item.IncomeSelf = l_temp

        l_temp = round(order_item.IncomeSelf * agent.Agent2rdPerc, 2)
        if not order_item.ShareUp1 == l_temp:
            update_flag = True
            order_item.ShareUp1 = l_temp

        l_temp = round(order_item.IncomeSelf * agent.Agent3rdPerc, 2)
        if not order_item.ShareUp2 == l_temp:
            update_flag = True
            order_item.ShareUp2 = l_temp

        if update_flag == True:
            order_item.save(update_fields=['IncomeSelf', 'ShareUp1', 'ShareUp2'])


def CalculateIncome(agent, start, end):
    # 找货PID APP的PID没有下线关系，只有机器人PID有上下线关系
    agent_pid = agent.AgentId
    zhaohuo_pid = str(agent.ZhaohuoPid)
    app_pid = str(agent.AppPid)

    # 个人订单收入
    aggregated1 = AliOrd.objects.filter(PosID=agent_pid, SettleDate__range=(start, end)).aggregate(
        Income=Sum('RebateAmt'))
    if aggregated1['Income'] == None:
        income_agent = 0
    else:
        income_agent = aggregated1['Income'] * agent.AgentPerc

    # 个人找货订单收入
    aggregated1 = AliOrd.objects.filter(PosID=zhaohuo_pid, SettleDate__range=(start, end)).aggregate(
        Income=Sum('RebateAmt'))
    if aggregated1['Income'] == None:
        income_zhaohuo = 0
    else:
        income_zhaohuo = aggregated1['Income'] * agent.AgentPerc

    # 个人APP订单收入
    aggregated1 = AliOrd.objects.filter(PosID=app_pid, SettleDate__range=(start, end)).aggregate(
        Income=Sum('RebateAmt'))
    if aggregated1['Income'] == None:
        income_app = 0
    else:
        income_app = aggregated1['Income'] * agent.AgentPerc

    agent.IncomeAgent = income_agent
    agent.IncomeZhaohuo = income_zhaohuo
    agent.IncomeApp = income_app

    agent.IncomeSelf = income_agent + income_zhaohuo + income_app

    # ##################下线佣金计算#################################
    # # 一级下线贡献佣金
    # aggregatedLv1 = AliOrd.objects.filter(UplineId=agent_pid, SettleDate__range=(start, end)).aggregate(
    #     IncomeLv1=Sum('ShareUp1'))
    #
    # # #新算法
    # # aggregatedLv1_new = AliOrd.objects.filter(UplineId=agent_pid, SettleDate__range=(start, end)).aggregate(
    # #     IncomeLv1=Sum('RebateAmt'))
    # #
    # # #l_temp = round(order_item.IncomeSelf * agent.Agent2rdPerc, 2)
    # # aggregatedLv1_new = aggregatedLv1_new**agent.Agent2rdPerc
    #
    # if aggregatedLv1['IncomeLv1'] == None:
    #     agent.IncomeLv1 = 0
    # else:
    #     agent.IncomeLv1 = aggregatedLv1['IncomeLv1']
    #
    # # 二级下线贡献佣金
    # aggregatedLv2 = AliOrd.objects.filter(Up2lineId=agent_pid, SettleDate__range=(start, end)).aggregate(
    #     IncomeLv2=Sum('ShareUp2'))
    # if aggregatedLv2['IncomeLv2'] == None:
    #     agent.IncomeLv2 = 0
    # else:
    #     agent.IncomeLv2 = aggregatedLv2['IncomeLv2']
    #
    # # 总佣金
    # agent.IncomeTotal = agent.IncomeSelf + agent.IncomeLv1 + agent.IncomeLv2
    # #agent.CalculateStatus = 'CPL'
    #
    # 保存计算结果
    # agent.save()

def sumup_pay_result(agent, start, end):
    ##################下线佣金计算#################################
    # 一级下线贡献佣金
    aggregatedLv1 = AliOrd.objects.filter(UplineId=agent_pid, SettleDate__range=(start, end)).aggregate(
        IncomeLv1=Sum('ShareUp1'))

    if aggregatedLv1['IncomeLv1'] == None:
        agent.IncomeLv1 = 0
    else:
        agent.IncomeLv1 = aggregatedLv1['IncomeLv1']

    # 二级下线贡献佣金
    aggregatedLv2 = AliOrd.objects.filter(Up2lineId=agent_pid, SettleDate__range=(start, end)).aggregate(
        IncomeLv2=Sum('ShareUp2'))
    if aggregatedLv2['IncomeLv2'] == None:
        agent.IncomeLv2 = 0
    else:
        agent.IncomeLv2 = aggregatedLv2['IncomeLv2']

    # 总佣金
    agent.IncomeTotal = agent.IncomeSelf + agent.IncomeLv1 + agent.IncomeLv2


def save_pay_result(agent, start, end):
    if not start == None:
        year = start.strftime('%Y')
        month = start.strftime('%m')

        updatedict={'AgentId':        str(agent.AgentId) if agent.AgentId else "",
                    'AgentName':      agent.AgentId.AgentName if agent.AgentId else "",
                    'AgentUpId':      str(agent.AgentUpId) if agent.AgentUpId else "",
                    'AgentUpName':    agent.AgentUpId.AgentName if agent.AgentUpId else "",
                    'AgentPerc':      agent.AgentPerc,
                    'Agent2rdPerc':   agent.Agent2rdPerc,
                    'Agent3rdPerc':   agent.Agent3rdPerc,
                    'ZhaohuoPid':     str(agent.ZhaohuoPid) if agent.ZhaohuoPid else "",
                    'ZhaohuoName':    agent.ZhaohuoPid.AgentName if agent.ZhaohuoPid else "",
                    'AppPid':         str(agent.AppPid) if agent.AppPid else "",
                    'AppName':        agent.AppPid.AgentName if agent.AppPid else "",
                    'GroupId':        agent.GroupId,
                    'IncomeAgent':    agent.IncomeAgent,
                    'IncomeZhaohuo':  agent.IncomeZhaohuo,
                    'IncomeApp':      agent.IncomeApp,
                    'IncomeSelf':     agent.IncomeSelf,
                    'IncomeLv1':      agent.IncomeLv1,
                    'IncomeLv2':      agent.IncomeLv2,
                    'IncomeTotal':    agent.IncomeTotal,
                    'Slug':           agent.Slug,
                    'CalculateStatus': agent.CalculateStatus,
                    'CalculateYear':  year,
                    'CalculateMonth': month}

        PayResult.objects.update_or_create(
            AgentId=agent.AgentId, CalculateYear=year, CalculateMonth=month,
            defaults=updatedict)

def save_sumup_result(agent, start, end):
    try:
        if not start == None:
            year = start.strftime('%Y')
            month = start.strftime('%m')

            PayResult.objects.filter(AgentId=agent.AgentId, CalculateYear=year, CalculateMonth=month).update(
                IncomeLv1=agent.IncomeLv1,
                IncomeLv2=agent.IncomeLv2,
                IncomeTotal=agent.IncomeTotal)
    except ObjectDoesNotExist:
        pass



def excel_add_sheet(ws, context_dict):
    style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',
                         num_format_str='#,##0.00')
    line_0 = [u'淘宝订单号', u'订单创建时间', u'订单结算时间', u'商品信息', u'商品类目', u'商品数量', u'商品单价',
              u'订单状态', u'订单类型', u'付款金额', u'代理ID', u'代理', u'代理上线ID', u'代理上线', u'佣金金额']
    # 生成第一行
    for i in range(0, len(line_0)):
        ws.write(0, i, line_0[i], style0)
    line_num = 1
    for line in context_dict:
        ws.write(line_num, 0, line.OrderId)
        ws.write(line_num, 1, line.CreatDate)
        ws.write(line_num, 2, line.SettleDate)
        ws.write(line_num, 3, line.CommType)
        ws.write(line_num, 4, line.Category)
        ws.write(line_num, 5, line.CommQty)
        ws.write(line_num, 6, line.CommPrice)
        ws.write(line_num, 7, line.OrdStatus)
        ws.write(line_num, 8, line.OrdType)
        ws.write(line_num, 9, line.PayAmount)
        ws.write(line_num, 10, line.PosID)
        ws.write(line_num, 11, line.PosName)
        ws.write(line_num, 12, line.UplineId)
        ws.write(line_num, 13, line.UplineName)
        ws.write(line_num, 14, line.IncomeSelf)

        line_num = line_num + 1

def get_date(function):
    now = datetime.datetime.now()

    if function == 'last_month_start':
        this_month_start = datetime.datetime(now.year, now.month, 1)
        last_month_end = this_month_start - datetime.timedelta(days=1)
        last_month_start = datetime.datetime(last_month_end.year, last_month_end.month, 1)
        return last_month_start.date()

    if function == 'last_month_end':
        this_month_start = datetime.datetime(now.year, now.month, 1)
        last_month_end = this_month_start - datetime.timedelta(days=1)
        return last_month_end.date()


def call_thread(mylog, agent, start, end):
    #mylog = logging.getLogger('mylog.file')
    try:
        # 计算所有订单佣金 volume 20000+
        CalculateOrderAgent(agent, start, end)

        # 分别计算机器人,找货，APP的订单
        agent_pid = agent.AgentId
        orders = AliOrd.objects.filter(PosID=agent_pid, SettleDate__range=(start, end))
        CalculateOrderAmount(agent, orders)

        # ZhaohuoPid can be None type
        agent_pid = str(agent.ZhaohuoPid)
        orders = AliOrd.objects.filter(PosID=agent_pid, SettleDate__range=(start, end))
        CalculateOrderAmount(agent, orders)

        agent_pid = str(agent.AppPid)
        orders = AliOrd.objects.filter(PosID=agent_pid, SettleDate__range=(start, end))
        CalculateOrderAmount(agent, orders)

        # 遍历所有 代理 计算 2
        # 计算收入 个人订单收入 + 一级下线贡献佣金 + 二级下线贡献佣金
        CalculateIncome(agent, start, end)

    except DatabaseError as err:
        my_msg = str(agent.AgentId.AgentName)+' '+str(agent.AgentId)+' '+str(err)
        mylog.warning(my_msg)

    except ObjectDoesNotExist as err:
        my_msg = str(agent.AgentId.AgentName)+' '+str(agent.AgentId)+' '+str(err)
        mylog.warning(my_msg)

    else:
        # 计算成功
        my_msg = str(agent.AgentId.AgentName)+' '+str(agent.AgentId) + ' 计算成功'
        mylog.warning(my_msg)

        agent.CalculateStatus = 'CPL'
        # 保存月佣金计算记录
        save_pay_result(agent, start, end)