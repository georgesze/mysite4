from django.conf.urls import include,url

from myapp import views
from myapp import upld as upld_views
from myapp import payslip as payslip_views
from myapp import transfer as transfer_views
import myapp

urlpatterns = [
    url(r'^$',views.dashboard),
    url(r'^upload/$', upld_views.upld),
    url(r'^payslip/$', payslip_views.AgentList),
    url(r'^transfer/$', transfer_views.AliTransfer),
    url(r'^payslip/(?P<agent_name_slug>[\w\-]+)/$', payslip_views.AgentDetail, name='Agent'),
]