from django.db import models
from django.contrib.auth.models import AbstractUser


class Users(AbstractUser):
    '''用户'''
    real_name = models.CharField(max_length=15, blank=True)
    nick_name = models.CharField(max_length=50, blank=True)
    avatar = models.URLField(blank=True)
    # 所属俱乐部
    clubs = models.ManyToManyField('football.Clubs')


class Clubs(models.Model):
    '''俱乐部'''
    club_name = models.CharField(max_length=50)
    brief = models.TextField(blank=True)
    # 成员
    members = models.ManyToManyField('football.Users')


class Games(models.Model):
    '''足球比赛'''
    start_time = models.DateTimeField(null=True)
    # 场地
    site = models.CharField(max_length=50)
    brief = models.TextField(blank=True)