from django.db import models
from django.contrib.auth.models import AbstractUser


class Users(AbstractUser):
    '''用户'''
    open_id = models.CharField(max_length=100, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    real_name = models.CharField(max_length=15, blank=True)
    nick_name = models.CharField(max_length=50, blank=True)
    # 常用名
    common_name = models.CharField(max_length=50, blank=True)
    avatar = models.URLField(blank=True)
    # 所属俱乐部
    clubs = models.ManyToManyField(
        'football.Clubs', related_name='users_set', through='football.UsersClubs')

    class Meta:
        db_table = 'fb_users'


class Clubs(models.Model):
    '''俱乐部'''
    club_name = models.CharField(max_length=50)
    club_logo = models.TextField(blank=True)
    # 创建者
    creator = models.ForeignKey(
        'football.Users', related_name='clubs_set1', on_delete=models.DO_NOTHING, null=True)
    # 队长
    captain = models.ForeignKey(
        'football.Users', related_name='clubs_set2', on_delete=models.DO_NOTHING, null=True)
    brief = models.TextField(blank=True)
    # 排序
    sort = models.IntegerField(default=0)
    # 荣誉值
    honor = models.IntegerField(default=0)
    # 加入是否需要审核
    need_apply = models.BooleanField(default=True)
    # 成员
    members = models.ManyToManyField(
        'football.Users', related_name='clubs_set', through='football.UsersClubs')
    # 场地
    playgrounds = models.ManyToManyField(
        'football.Playgrounds', related_name='clubs_set', through='football.ClubsPlayground')

    class Meta:
        db_table = 'fb_clubs'
        ordering = ('id',)


class UsersClubs(models.Model):
    '''用户<==>俱乐部，多对多中间表'''
    user = models.ForeignKey(
        'football.Users', related_name='users_clubs_set', on_delete=models.CASCADE)
    club = models.ForeignKey(
        'football.Clubs', related_name='users_clubs_set', on_delete=models.CASCADE)
    # 用户在俱乐部中的角色， 1：超级管理  2：管理员  3：会员
    role = models.IntegerField(default=3)

    class Meta:
        db_table = 'fb_users_clubs'


class ClubsPlayground(models.Model):
    '''俱乐部<==>场地，多对多中间表'''
    playground = models.ForeignKey(
        'football.Playgrounds', related_name='clubs_playground_set', on_delete=models.CASCADE)
    club = models.ForeignKey(
        'football.Clubs', related_name='clubs_playground_set', on_delete=models.CASCADE)
    # 俱乐部场地的额外字段：优惠类型  0：无优惠  1：押金优惠 2：充值优惠
    preferential = models.IntegerField(default=0)

    class Meta:
        db_table = 'fb_clubs_playground'


class Account(models.Model):
    '''优惠账户'''
    # 余额
    balance = models.FloatField(blank=True)
    # 对应用户
    user = models.ForeignKey('football.Users', on_delete=models.CASCADE)
    # 对应俱乐部
    club = models.ForeignKey('football.Clubs', on_delete=models.CASCADE)

    class Meta:
        db_table = 'fb_account'


class Games(models.Model):
    '''足球比赛'''
    # 标题
    title = models.CharField(max_length=50)
    # 时间
    start_time = models.DateTimeField(null=True)
    # 场地
    site = models.CharField(max_length=50, null=True)
    # 最小人数：几人制
    mix_people = models.IntegerField(default=0)
    # 最大报名人数
    max_people = models.IntegerField(default=0)
    # 是否公开约战
    open_battle = models.BooleanField(default=False)
    # 实价
    price = models.FloatField(default=0, blank=True)
    # 原价
    original_price = models.FloatField(default=0, blank=True)
    # 其它费用
    cost = models.FloatField(default=0, blank=True)
    # 比赛状态  0：比赛中  1：未结算  2：比赛结束
    status = models.IntegerField(default=0)
    # 简介
    brief = models.TextField(blank=True)
    # 分组
    group = models.IntegerField(default=1)
    # 约战对象
    battle = models.OneToOneField(
        'football.Games', on_delete=models.DO_NOTHING, null=True)
    # 对应球队
    club = models.ForeignKey(
        'football.Clubs', on_delete=models.CASCADE, null=True)
    # 参赛人员
    members = models.ForeignKey(
        'football.GameMembers',  on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'fb_games'
        ordering = ('id',)


class GameMembers(models.Model):
    '''比赛报名人员'''
    # 备注
    remarks = models.CharField(max_length=30, null=True)
    # 进球数
    goal = models.IntegerField(default=0)
    # 所属比赛
    game = models.ForeignKey(
        'football.Games', on_delete=models.CASCADE, null=True)
    group = models.IntegerField(default=0)
    # 费用
    cost = models.FloatField(null=True)
    user = models.ForeignKey(
        'football.Users', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'fb_game_members'


class Apply(models.Model):
    '''申请加入俱乐部'''
    # 申请时间
    created = models.DateTimeField(auto_now_add=True)
    # 备注
    remarks = models.TextField(max_length=50, null=True)
    # 申请人
    apply_user = models.ForeignKey(
        'football.Users', on_delete=models.CASCADE, null=True)
    # 申请要加入的俱乐部
    club = models.ForeignKey(
        'football.Clubs', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'fb_apply'
        ordering = ('id',)


class Playgrounds(models.Model):
    '''球场'''
    playground_name = models.CharField(max_length=30)
    # 球场类型 1：足球  2：篮球  3：羽毛球  4：乒乓球
    play_type = models.IntegerField(default=1)
    # 省
    province = models.CharField(max_length=20, null=True)
    # 市
    city = models.CharField(max_length=20, null=True)
    # 区
    region = models.CharField(max_length=20, null=True)
    # 详细地址
    address = models.TextField(null=True)

    class Meta:
        db_table = 'fb_playground'
        ordering = ('id',)


class UploadImages(models.Model):
    '''上传的图片'''
    height = models.PositiveIntegerField(default=75)
    width = models.PositiveIntegerField(default=75)
    image_type = models.IntegerField(default=1)
    image_url = models.ImageField(
        upload_to='upload', height_field='height', width_field='width')

    class Meta:
        db_table = 'fb_upload_imges'
