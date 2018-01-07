#coding:utf-8 
from django.contrib import admin

# Register your models here.
from myapp.models import AliOrd, AliConfig, Agent, PayResult

# Add in this class to customized the Admin Interface
class AliOrdAdmin(admin.ModelAdmin):
    list_display = ('CommId', 'CommPrice', 'PayAmount','SettleDate','RebateAmt','OrderId','PosName','UplineName','Up2lineName',)

class AliConfigAdmin(admin.ModelAdmin):
    list_display = ('GroupId', 'AgentId', 'AgentUpId', 'ZhaohuoPid', 'AppPid', 'AgentPerc', 'Agent2rdPerc', 'Agent3rdPerc',)

class AgentAdmin(admin.ModelAdmin):
    list_display = ('AgentName', 'AgentId',)

class PayResultAdmin(admin.ModelAdmin):
    list_display = ('GroupId', 'AgentName', 'AgentId', 'AgentUpName', 'AgentUpId', 'ZhaohuoPid', 'AppPid', 'AgentPerc', 'Agent2rdPerc', 'Agent3rdPerc',
                    'IncomeSelf', 'IncomeLv1', 'IncomeLv2', 'IncomeTotal', 'CalculateStatus', 'CalculateYear', 'CalculateMonth', 'PayAccount', 'PayStatus',)

admin.site.register(AliOrd, AliOrdAdmin)
admin.site.register(AliConfig, AliConfigAdmin)
admin.site.register(Agent, AgentAdmin)
admin.site.register(PayResult, PayResultAdmin)