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
        'football.Clubs', related_name='clubs_set', through='football.UsersClubs')

    class Meta:
        db_table = 'fb_users'


class Clubs(models.Model):
    '''俱乐部'''
    club_name = models.CharField(max_length=50)
    club_logo = models.TextField(blank=True)
    brief = models.TextField(blank=True)
    # 排序
    sort = models.IntegerField(default=0)
    # 荣誉值
    honor = models.IntegerField(default=0)
    # 加入是否需要审核
    need_apply = models.BooleanField(default=True)
    # 成员
    members = models.ManyToManyField(
        'football.Users', related_name='users_set', through='football.UsersClubs')

    class Meta:
        db_table = 'fb_clubs'


class UsersClubs(models.Model):
    '''用户<==>俱乐部，多对多中间表'''
    use = models.ForeignKey(
        'football.Users',  on_delete=models.CASCADE)
    club = models.ForeignKey(
        'football.Clubs',  on_delete=models.CASCADE)
    # 用户在俱乐部中的角色， 1：超级管理  2：管理员  3：会员
    role = models.IntegerField(default=3)

    class Meta:
        db_table = 'fb_users_clubs'


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
    site = models.CharField(max_length=50)
    # 实价
    price = models.FloatField(blank=True)
    # 原价
    original_price = models.FloatField(blank=True)
    # 费用
    cost = models.FloatField(blank=True)
    # 简介
    brief = models.TextField(blank=True)
    # 分组
    group = models.IntegerField(default=1)
    # 参赛人员
    members = models.ForeignKey(
        'football.GameMembers',  on_delete=models.CASCADE)

    class Meta:
        db_table = 'fb_games'


class GameMembers(models.Model):
    '''比赛报名人员'''
    name = models.CharField(max_length=30)
    # 进球数
    goal = models.IntegerField(default=0)
    # 所属比赛
    game = models.ForeignKey(
        'football.Games', on_delete=models.CASCADE)
    group = models.IntegerField(default=0)
    # 费用
    cost = models.FloatField(blank=True)

    class Meta:
        db_table = 'fb_game_members'


class Apply(models.Model):
    '''申请加入俱乐部'''
    # 申请时间
    created = models.DateTimeField(auto_now_add=True)
    # 申请人姓名
    applicant_name = models.CharField(max_length=15, blank=True)
    # 常用称呼
    common_name = models.CharField(max_length=15, blank=True)
    # 申请要加入的俱乐部
    club = models.ForeignKey(
        'football.Clubs', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'fb_apply'


class UploadImages(models.Model):
    '''上传的图片'''
    height = models.PositiveIntegerField(default=75)
    width = models.PositiveIntegerField(default=75)
    image_type = models.IntegerField(default=1)
    image_url = models.ImageField(
        upload_to='upload', height_field='height', width_field='width')

    class Meta:
        db_table = 'fb_upload_imges'
