from django.db import models
from django.contrib.auth.models import AbstractUser
from common.utils import get_upload_to
from datetime import datetime

class Users(AbstractUser):
    '''用户'''
    open_id = models.CharField(max_length=100, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    real_name = models.CharField(max_length=15, blank=True)
    nick_name = models.CharField(max_length=50, blank=True)
    avatar = models.URLField(blank=True)

    class Meta:
        db_table = 'bt_users'

class UsersHonor(models.Model):
    '''用户荣誉'''
    year = models.CharField(max_length=4, default=datetime.now().strftime('%Y'))
    month = models.IntegerField(default=datetime.now().month)
    user = models.ForeignKey(
        'battle.Users', related_name='users_honor_set', on_delete=models.CASCADE)
    club = models.ForeignKey(
        'battle.Clubs', related_name='users_honor_set', on_delete=models.CASCADE)
    # 荣誉值
    honor = models.IntegerField(default=0, blank=True)
    # 进球数
    goal = models.IntegerField(default=0, blank=True)
    # 外战进球数
    goal_out = models.IntegerField(default=0, blank=True)
    # 助攻次数
    assist = models.IntegerField(default=0, blank=True)
    # 外战助攻次数
    assist_out = models.IntegerField(default=0, blank=True)
    # 贡献
    contribute = models.IntegerField(default=0, blank=True)
    # mvp次数
    mvp = models.IntegerField(default=0, blank=True)

    class Meta:
        db_table = 'bt_users_honor'


class Clubs(models.Model):
    '''俱乐部'''
    club_name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=8, null=True)
    club_logo = models.TextField(blank=True)
    area = models.CharField(max_length=50, null=True)
    area_code = models.CharField(max_length=50, null=True)
    # 随机码
    code = models.CharField(max_length=24, null=True)
    # 创建者
    creator = models.ForeignKey(
        'battle.Users', related_name='clubs_set1', on_delete=models.DO_NOTHING, null=True)
    # 类型 1:足球  2：篮球
    club_type = models.IntegerField(default=1)
    brief = models.TextField(blank=True)
    # 排序
    sort = models.IntegerField(default=0)
    # 荣誉值
    honor = models.IntegerField(default=0)
    # 信誉值
    credit = models.IntegerField(default=0)
    # 完赛场次
    game_total = models.IntegerField(default=0)
    # 加入是否需要审核
    need_apply = models.BooleanField(default=True)
    # 热门
    hot = models.BooleanField(default=False)
    # 成员
    members = models.ManyToManyField(
        'battle.Users', related_name='clubs_set', through='battle.UsersClubs')
    # 主场
    main_playground = models.CharField(max_length=50, blank=True, default='')
    # 场地
    playgrounds = models.ManyToManyField(
        'battle.Playgrounds', related_name='clubs_set', through='battle.ClubsPlaygrounds')

    class Meta:
        db_table = 'bt_clubs'
        ordering = ('id',)


class UsersClubs(models.Model):
    '''用户<==>俱乐部，多对多中间表'''
    user = models.ForeignKey(
        'battle.Users', related_name='users_clubs_set', on_delete=models.CASCADE)
    club = models.ForeignKey(
        'battle.Clubs', related_name='users_clubs_set', on_delete=models.CASCADE)
    # 用户在俱乐部中的角色， 1：超级管理  2：管理员  3：会员
    role = models.IntegerField(default=3)
    # 分队
    group = models.IntegerField(default=999)

    class Meta:
        db_table = 'bt_users_clubs'


class Games(models.Model):
    '''足球比赛'''
    # 创建者
    creator = models.ForeignKey(
        'battle.Users', on_delete=models.DO_NOTHING, null=True)
    # 标题
    title = models.CharField(max_length=50, null=True, blank=True)
    # 标签
    tag = models.CharField(max_length=10, null=True, blank=True)
    # 比赛开始时间
    start_time = models.DateTimeField(null=True, blank=True)
    # 比赛结束时间
    end_time = models.DateTimeField(null=True, blank=True)
    # 场地
    playground = models.ForeignKey(
        'battle.Playgrounds', on_delete=models.DO_NOTHING, blank=True, null=True)
    # 最小人数：几人制
    min_people = models.IntegerField(default=0, null=True, blank=True,)
    # 最大报名人数
    max_people = models.IntegerField(default=0, null=True, blank=True,)
    # 对手最少人数限制
    competition = models.IntegerField(default=0, null=True, blank=True,)
    # 取消报名时间
    cancel_time = models.IntegerField(default=0, null=True, blank=True,)
    # 是否公开约战
    open_battle = models.BooleanField(default=False)
    # 优惠价
    price = models.FloatField(blank=True)
    # 原价
    original_price = models.FloatField(blank=True)
    # 其它费用
    cost = models.FloatField(blank=True)
    # 比赛状态  0：比赛中  1：比赛结束
    status = models.IntegerField(default=0)
    # 比赛类型  1：内战 2：外战 3:自由
    game_type = models.IntegerField(default=1)
    # 简介
    brief = models.TextField(blank=True)
    # 分组
    group = models.IntegerField(default=1)
    # 自定义约战对象
    battle_name = models.CharField(max_length=20, null=True, blank=True)
    # 自定义约战对象进球数
    battle_goal = models.IntegerField(default=0, null=True, blank=True,)
    # 约战对象
    battle = models.OneToOneField(
        'battle.Games', on_delete=models.DO_NOTHING, null=True)
    # 对应球队
    club = models.ForeignKey(
        'battle.Clubs', on_delete=models.CASCADE, null=True)
    # 留言
    remarks = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'bt_games'
        ordering = ('id',)


class GameMembers(models.Model):
    '''比赛报名人员'''
    # 备注
    remarks = models.CharField(max_length=30, blank=True,  null=True)
    # 进球数
    goal = models.IntegerField(default=0)
    # 助攻
    assist = models.IntegerField(default=0)
    # mvp
    mvp = models.IntegerField(default=0)
    # 分组
    group = models.IntegerField(default=0)
    # 费用
    cost = models.CharField(max_length=50, blank=True,  null=True)
    # 是否免费
    free = models.BooleanField(default=False)
    # 所属球队
    club = models.ForeignKey(
        'battle.Clubs', on_delete=models.CASCADE, null=True)
    # 所属比赛
    game = models.ForeignKey(
        'battle.Games', on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(
        'battle.Users', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'bt_game_members'


class Apply(models.Model):
    '''申请加入俱乐部'''
    # 申请时间
    created = models.DateTimeField(auto_now_add=True)
    # 备注
    remarks = models.TextField(max_length=50, null=True)
    # 申请人
    apply_user = models.ForeignKey(
        'battle.Users', on_delete=models.CASCADE, null=True)
    # 申请要加入的俱乐部
    club = models.ForeignKey(
        'battle.Clubs', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'bt_apply'
        ordering = ('id',)


class BattleApply(models.Model):
    '''申请应战'''
    # 申请时间
    created = models.DateTimeField(auto_now_add=True)
    # 备注
    remarks = models.TextField(max_length=50, null=True)
    # 自己
    game = models.ForeignKey(
        'battle.Games', related_name='game_set1', on_delete=models.CASCADE, null=True)
    # 对手
    rival = models.ForeignKey(
        'battle.Games', related_name='game_set2', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'bt_battle_apply'
        ordering = ('id',)


class Playgrounds(models.Model):
    '''球场'''
    playground_name = models.CharField(max_length=30)
    # 球场类型 1：足球  2：篮球  3：羽毛球  4：乒乓球
    play_type = models.IntegerField(default=1)
    area = models.CharField(max_length=50, null=True)
    area_code = models.CharField(max_length=50, null=True)
    # 详细地址
    address = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'bt_playground'
        ordering = ('id',)


class ClubsPlaygrounds(models.Model):
    '''俱乐部<==>场地，多对多中间表'''
    playground = models.ForeignKey(
        'battle.Playgrounds', related_name='clubs_playground_set', on_delete=models.CASCADE)
    club = models.ForeignKey(
        'battle.Clubs', related_name='clubs_playground_set', on_delete=models.CASCADE)
    # 主场
    main = models.BooleanField(default=False)

    class Meta:
        db_table = 'bt_clubs_playgrounds'


class Account(models.Model):
    '''个人账户'''
    # 余额
    balance = models.FloatField(blank=True)
    # 账户类型  1:充值   2：押金
    account_type = models.IntegerField(default=1, blank=True)
    # 对应用户
    user = models.ForeignKey('battle.Users', on_delete=models.CASCADE)
    # 对应俱乐部
    club = models.ForeignKey('battle.Clubs', on_delete=models.DO_NOTHING)
    # 对应球场
    playground = models.ForeignKey(
        'battle.Playgrounds', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'bt_account'


class AccountRecord(models.Model):
    '''充值和消费记录'''
    # 金额
    amount = models.FloatField(blank=True)
    # 动账类型  1:充值   2：消费
    amount_type = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    # 对应比赛
    game = models.ForeignKey(
        'battle.Games', on_delete=models.DO_NOTHING, blank=True, null=True)
    # 对应用户
    user = models.ForeignKey(
        'battle.Users', on_delete=models.CASCADE, blank=True, null=True)
    # 对应俱乐部
    club = models.ForeignKey('battle.Clubs', on_delete=models.DO_NOTHING)
    # 对应球场
    playground = models.ForeignKey(
        'battle.Playgrounds', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'bt_account_record'


class ClubAccount(models.Model):
    '''球队账户'''
    # 余额
    balance = models.FloatField(blank=True)
    # 账户类型  1:充值   2：押金
    account_type = models.IntegerField(default=1, blank=True)
    # 对应俱乐部
    club = models.ForeignKey('battle.Clubs', on_delete=models.CASCADE)
    # 对应球场
    playground = models.ForeignKey(
        'battle.Playgrounds', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'bt_club_account'


class UploadImages(models.Model):
    '''上传的图片'''
    height = models.PositiveIntegerField(default=155)
    width = models.PositiveIntegerField(default=155)
    # 图片所属用户
    user = models.ForeignKey(
        'battle.Users', on_delete=models.CASCADE, blank=True, null=True)
    image_type = models.IntegerField(default=0)
    image_url = models.ImageField(
        upload_to=get_upload_to, height_field='height', width_field='width')

    class Meta:
        db_table = 'bt_upload_imges'


class Advert(models.Model):
    '''广告位'''
    # 标题
    title = models.CharField(max_length=30, blank=True)
    # 上架状态
    status = models.BooleanField(default=False)
    # 所在列
    row = models.IntegerField(default=1)
    # 图片
    ad_pic = models.TextField(blank=True)
    # 图片高度
    ad_pic_height = models.IntegerField(default=0)
    # 广告位置类型  0：banner, 1:首页中间位置
    ad_type = models.IntegerField(default=0)
    # 跳转类型  0:不跳转 1：H5  2:小程序页面
    jump_type = models.IntegerField(default=0)
    # 跳转地址
    jump_url = models.TextField(blank=True)

    class Meta:
        db_table = 'bt_advert'


class Message(models.Model):
    '''消息中心'''
    # 消息
    message = models.TextField(blank=True)
    # 信息类型  1：反馈给站长  2：反馈给管理员  3：系统公告
    m_type = models.IntegerField(default=1)
    # 回复
    reply = models.TextField(blank=True)
    # 创建时间
    created = models.DateTimeField(auto_now_add=True)
    # 回复时间
    reply_time = models.DateTimeField(null=True)
    # 是否已读
    readed = models.BooleanField(default=False)
    # 创建者
    owner = models.ForeignKey(
        'battle.Users', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'bt_messages'
