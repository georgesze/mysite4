#coding:utf-8

from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from myapp.models import AliConfig, AliOrd, PayResult

import csv
import xlwt

def AliTransfer(request):
    current_payslip = {}
    month_picker = ''

    if (request.method == "POST") and ('display_payslip' in request.POST):
        month_picker = request.POST.get('month_picker')
        current_year = month_picker[0:4]
        current_month = month_picker[5:7]

        current_payslip = PayResult.objects.filter(CalculateYear=current_year, CalculateMonth=current_month)

    elif (request.method == "POST") and ('generate_transfer' in request.POST):
        check_list = request.POST.getlist('selected')
        if check_list:
            transfer_list = PayResult.objects.filter(pk__in=check_list)

            wb = xlwt.Workbook()

            ws = wb.add_sheet('付款')
            # style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',
            #                      num_format_str='#,##0.00')
            line_0 = [u'批次号', u'付款日期', u'付款人email', u'账户名称', u'总金额（元）', u'总笔数']
            # 生成第一行
            for i in range(0, len(line_0)):
                ws.write(0, i, line_0[i])

            line_1 = [u'', u'', u'wealth_public@163.com', u'上海威欧氏贸易有限公司']
            # 生成第二行
            for i in range(0, len(line_1)):
                ws.write(1, i, line_1[i])

            # 生成第三行
            line_2 = [u'商户流水号', u'收款人email', u'收款人姓名', u'付款金额（元）', u'付款理由']
            for i in range(0, len(line_2)):
                ws.write(2, i, line_2[i])

            # 生成明细行
            line_num = 3
            line_count = 1
            for agent in transfer_list:
                ws.write(line_num, 0, str(line_count))
                ws.write(line_num, 1, str(agent.PayAccount))
                ws.write(line_num, 2, str(agent.PayAccount))
                ws.write(line_num, 3, str(agent.IncomeTotal))
                ws.write(line_num, 4, '佣金')

                line_num = line_num + 1
                line_count = line_count + 1

            response = HttpResponse(content_type='application/msexcel')
            response['Content-Disposition'] = 'attachment; filename=agents.csv'
            wb.save(response)
            return response

    return render(request, 'myapp/transfer.html', {'form_payslip': current_payslip,
                                                    'month_picker': month_picker})
