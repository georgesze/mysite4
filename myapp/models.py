# coding:utf-8
from django.db import models
from django.template.defaultfilters import default, slugify
from django.forms.widgets import Media


# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=30)
    headImg = models.FileField(upload_to='./upload/')

    def __str__(self):
        return self.username


class AliOrd(models.Model):
    CreatDate = models.DateTimeField(verbose_name='创建时间', default='')
    ClickDate = models.DateTimeField(verbose_name='点击时间', default='')
    CommType = models.CharField(max_length=40, verbose_name='商品信息', default='')
    CommId = models.CharField(max_length=20, verbose_name='商品ID', default='')
    WangWangId = models.CharField(max_length=20, verbose_name='掌柜旺旺', default='')
    StoreId = models.CharField(max_length=20, verbose_name='所属店铺', default='')
    CommQty = models.CharField(max_length=20, verbose_name='商品数', default='')
    CommPrice = models.CharField(max_length=20, verbose_name='商品单价', default='')
    OrdStatus = models.CharField(max_length=20, verbose_name='订单状态', default='')
    OrdType = models.CharField(max_length=20, verbose_name='订单类型', default='')
    IncomePerc = models.CharField(max_length=8, verbose_name='收入比率', default='')
    DividePerc = models.CharField(max_length=8, verbose_name='分成比率', default='')
    PayAmount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='付款金额')
    EstAmount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='预估效果')
    SettleAmt = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='结算金额')
    EstIncome = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='预估收入')
    SettleDate = models.DateTimeField(verbose_name='结算时间', default='')
    RebatePerc = models.CharField(max_length=8, verbose_name='佣金比例', default='')
    RebateAmt = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='佣金金额')
    AllowancePerc = models.CharField(max_length=8, verbose_name='补贴比例', default='')
    AllowanceAmt = models.CharField(max_length=8, verbose_name='补贴金额', default='')
    AllowanceType = models.CharField(max_length=20, verbose_name='补贴类型', default='')
    Platform = models.CharField(max_length=20, verbose_name='成交平台', default='')
    ThirdParty = models.CharField(max_length=20, verbose_name='第三方服务', default='')
    OrderId = models.CharField(max_length=20, verbose_name='订单编号', default='')
    Category = models.CharField(max_length=20, verbose_name='类目名称', default='')
    MediaId = models.CharField(max_length=20, verbose_name='来源媒体ID', default='')
    MediaName = models.CharField(max_length=20, verbose_name='来源媒体名称', default='')
    PosID = models.CharField(max_length=20, verbose_name='广告位ID', default='')
    PosName = models.CharField(max_length=20, verbose_name='广告位名称', blank=True, null=True)
    UplineId = models.CharField(max_length=20, verbose_name='上线ID', blank=True, null=True)
    UplineName = models.CharField(max_length=20, verbose_name='上线名称', blank=True, null=True)
    Up2lineId = models.CharField(max_length=20, verbose_name='上上线ID', blank=True, null=True)
    Up2lineName = models.CharField(max_length=20, verbose_name='上上线名称', blank=True, null=True)
    IncomePercSelf = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='自获佣金比例', blank=True, null=True)
    SharePercUp1 = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='贡献上级佣金比例', blank=True, null=True)
    SharePercUp2 = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='贡献上上级佣金比例', blank=True, null=True)
    IncomeSelf = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='自获佣金额', blank=True, null=True)
    ShareUp1 = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='贡献上级佣金额', blank=True, null=True)
    ShareUp2 = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='贡献上上级佣金额', blank=True, null=True)

    class Meta:
        verbose_name = '推广订单'
        verbose_name_plural = '推广订单'

    def __str__(self):
        return self.OrderId


class AliConfig(models.Model):
    class Meta:
        verbose_name = "代理配置"
        verbose_name_plural = "代理配置"

    AgentId = models.OneToOneField('Agent', related_name='AId', verbose_name='代理', default=None, blank=True, null=True)
    AgentName = models.CharField(max_length=20, verbose_name='代理名称', default=None, blank=True, null=True)
    AgentUpId = models.ForeignKey('Agent', related_name='AUpId', verbose_name='上线', default=None, blank=True, null=True)
    AgentUpName = models.CharField(max_length=20, verbose_name='上线名称', blank=True)
    AgentPerc = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='自获佣金比例')
    Agent2rdPerc = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='提取二级佣金比例')
    Agent3rdPerc = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='提取三级佣金比例')
    ZhaohuoPid = models.ForeignKey('Agent', related_name='ZhId', verbose_name='找货广告位', default=None, blank=True, null=True)
    ZhaohuoName = models.CharField(max_length=20, verbose_name='找货广告名称', default=None, blank=True, null=True)
    AppPid = models.ForeignKey('Agent', related_name='AppId', verbose_name='APP广告位', default=None, blank=True, null=True)
    AppName = models.CharField(max_length=20, verbose_name='APP广告位名称', default=None, blank=True, null=True)
    JDPid = models.ForeignKey('Agent', related_name='JDId', verbose_name='JD广告位', default=None, blank=True, null=True)
    JDName = models.CharField(max_length=20, verbose_name='JD广告位名称', default=None, blank=True, null=True)
    ZhaohuoPerc = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='找货佣金比例', blank=True, null=True)
    ZhaohuoBot = models.CharField(max_length=20, verbose_name='找货机器人', default='', blank=True)
    GroupId = models.CharField(max_length=20, verbose_name='团队合伙人', default='', blank=True)
    TopLevel = models.BooleanField(verbose_name='顶级账号', default=False, blank=True)
    Active = models.BooleanField(verbose_name='激活状态', default=False, blank=True)
    ValidBegin = models.DateField(verbose_name='有效期开始时间', blank=True, null=True)
    ValidEnd = models.DateField(verbose_name='有效期结束时间', blank=True, null=True)
    IncomeAgent = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='机器人佣金', blank=True, null=True)
    IncomeZhaohuo = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='找货佣金', blank=True, null=True)
    IncomeApp = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='APP佣金', blank=True, null=True)
    IncomeJD = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='京东佣金', blank=True, null=True)
    IncomeSelf = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='自获佣金额', blank=True, null=True)
    IncomeLv1 = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='下级贡献佣金', blank=True, null=True)
    IncomeLv2 = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='二级贡献佣金', blank=True, null=True)
    IncomeTotal = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='总佣金', blank=True, null=True)
    CalculateStatus = models.CharField(max_length=10, verbose_name='计算状态', default='', blank=True)
    Slug = models.SlugField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.AgentId is not None:
            self.Slug = slugify(self.AgentId)
            super(AliConfig, self).save(*args, **kwargs)
        elif self.ZhaohuoPid is not None:
            self.Slug = slugify(self.ZhaohuoPid)
            super(AliConfig, self).save(*args, **kwargs)
        elif self.AppPid is not None:
            self.Slug = slugify(self.AppPid)
            super(AliConfig, self).save(*args, **kwargs)

    def __str__(self):
        if self.AgentId is None:
            agent_name = ''
        else:
            agent_name = self.AgentId.AgentName
        return agent_name


class PayResult(models.Model):
    class Meta:
        verbose_name = "工资记录"
        verbose_name_plural = "工资记录"

    AgentId = models.CharField(max_length=20, verbose_name='代理ID', blank=True, null=True)
    AgentName = models.CharField(max_length=20, verbose_name='代理名称', default=None, blank=True, null=True)
    AgentUpId = models.CharField(max_length=20, verbose_name='上线ID', blank=True, null=True)
    AgentUpName = models.CharField(max_length=20, verbose_name='上线名称', blank=True)
    AgentPerc = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='自获佣金比例', null=True)
    Agent2rdPerc = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='提取二级佣金比例', null=True)
    Agent3rdPerc = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='提取三级佣金比例', null=True)
    ZhaohuoPid = models.CharField(max_length=20, verbose_name='找货广告位', default=None, blank=True, null=True)
    ZhaohuoName = models.CharField(max_length=20, verbose_name='找货名称', default=None, blank=True, null=True)
    AppPid = models.CharField(max_length=20, verbose_name='APP广告位', default=None, blank=True, null=True)
    AppName = models.CharField(max_length=20, verbose_name='APP广告位名称', default=None, blank=True, null=True)
    ZhaohuoPerc = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='找货佣金比例', blank=True, null=True)
    ZhaohuoBot = models.CharField(max_length=20, verbose_name='找货机器人', default='', blank=True, null=True)
    GroupId = models.CharField(max_length=20, verbose_name='组号', default='', blank=True, null=True)
    IncomeAgent = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='机器人佣金', blank=True, null=True)
    IncomeZhaohuo = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='找货佣金', blank=True, null=True)
    IncomeApp = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='APP佣金', blank=True, null=True)
    IncomeJD = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='京东佣金', blank=True, null=True)
    IncomeSelf = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='自获佣金额', blank=True, null=True)
    IncomeLv1 = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='下级贡献佣金', blank=True, null=True)
    IncomeLv2 = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='二级贡献佣金', blank=True, null=True)
    IncomeTotal = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='总佣金', blank=True, null=True)
    CalculateStatus = models.CharField(max_length=10, verbose_name='计算状态', default='', blank=True, null=True)
    CalculateYear = models.CharField(max_length=4, verbose_name='计算年份', default='', blank=True, null=True)
    CalculateMonth = models.CharField(max_length=2, verbose_name='计算月份', default='', blank=True, null=True)
    PayAccount = models.CharField(max_length=20, verbose_name='支付账号', blank=True, null=True)
    PayStatus = models.CharField(max_length=20, verbose_name='支付情况', blank=True, null=True)
    Slug = models.SlugField(blank=True, null=True)

    # def save(self, *args, **kwargs):
    #     str_agentid = str(self.AgentId)
    #     self.Slug = slugify(str_agentid)
    #     super(PayResult, self).save(*args, **kwargs)

    # def __str__(self):
    #     return self.AgentName

        # ===========================================================================
        # def publish(self):
        #     self.published_date = timezone.now()
        #     self.save()
        # def approved_commentimages(self):
        #     return self.comments.filter(approved_comment=True)
        # ===========================================================================


class Agent(models.Model):
    class Meta:
        verbose_name = "代理"
        verbose_name_plural = "代理"

    AgentId = models.CharField(max_length=20, verbose_name=u'代理广告位', unique=True)
    AgentName = models.CharField(max_length=20, verbose_name=u'代理名称', default='')

    def __str__(self):
        return self.AgentId
