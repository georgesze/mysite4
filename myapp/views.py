from django.shortcuts import render
from myapp.models import AliConfig, AliOrd, PayResult
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
import json,decimal
from django.core.serializers.json import DjangoJSONEncoder

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

# Create your views here.
def dashboard(request):
    customers = AliConfig.objects.all().order_by('AgentId')

    paginator = Paginator(customers, 25)    #每页显示2条
    page = request.GET.get('page')        #前段请求的页,比如点击'下一页',该页以变量'page'表示
    try:
      customer_obj = paginator.page(page) #获取前端请求的页数
    except PageNotAnInteger:
        customer_obj = paginator.page(1)   #如果前端输入的不是数字,就返回第一页
    except EmptyPage:
        customer_obj = paginator.page(paginator.num_pages)   #如果前端请求的页码超出范围,则显示最后一页.获取总页数,返回最后一页.比如共10页,则返回第10页.

    #q_orders = PayResult.objects.values('AgentName', 'IncomeTotal')
    queryset = PayResult.objects.values('AgentName').annotate(sum=Sum('IncomeTotal')).values_list('AgentName', 'sum')
    q_orders = json.dumps(list(queryset), cls=DecimalEncoder)

    return render(request, 'myapp/dashboard.html', {'customers_list': customer_obj,
                                                    'q_orders': q_orders
                                                    })

