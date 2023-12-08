import base64
import json
import urllib.request
import urllib.parse
from Cryptodome.Cipher import AES
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
import datetime
import random

# 解密微信手机号等信息


class WXBizDataCrypt:
    def __init__(self, appId, sessionKey):
        self.appId = appId
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)
        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)
        decrypted = json.loads(self._unpad(
            cipher.decrypt(encryptedData).decode()))

        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]


# 基本分页
class NewPagination(PageNumberPagination):

    page_size = 50
    max_page_size = 100
    page_size_query_param = 'pageSize'
    page_query_param = 'page'       # 查询的页数。

    def get_paginated_response(self, data):
        if self.page.has_next():
            next = self.page.next_page_number()
        else:
            next = ''
        return Response({
            'count': self.page.paginator.count,
            'next': next,
            # 'previous': self.page.paginator.page_range,
            # 'code': status.HTTP_200_OK,
            'message': 'ok',
            'results': data,
        })

# 偏移分页
# class NewPagination(LimitOffsetPagination):

#     default_limit = 5   # 显示多少条
#     limit_query_param = 'size'  # 每次取的条数
#     offset_query_param = 'page' # 如果page=6 表示从第6条可以查。
#     max_limit  = 50   # 最多取50条

# 游标分页
# class NewPagination(CursorPagination):

#     cursor_query_param = 'cursor'
#     # ordering = 'id'  # 按照id排序
#     page_size = 10  # 每页显示多少条
#     page_size_query_param = 'pageSize'  # 每页显示多少条、
#     max_page_size = 50    # 最多显示5条


def getSessionInfo(jsCode, appid, secret):
    url = "https://api.weixin.qq.com/sns/jscode2session?appid=" + appid + \
        "&secret=" + secret + "&js_code=" + jsCode + "&grant_type=authorization_code"
    res = urllib.request.urlopen(url)
    content = res.read().decode()
    obj = json.loads(content)
    return obj


def getAccessToken(appid, secret):
    url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + appid + \
        "&secret=" + secret
    access_token = cache.get('access_token')
    if not access_token:
        res = urllib.request.urlopen(url)
        content = res.read().decode()
        obj = json.loads(content)
        # 缓存起来,7200秒（两小时）有效
        cache.set('access_token', obj['access_token'], obj['expires_in'])
        return obj['access_token']
    else:
        return access_token


# 获取小程序二维码

def getUnlimited(access_token, params):
    url = "https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token=" + access_token

    # 使用urlencode将字典参数序列化成字符串
    data_string = json.dumps(params)
    # 将序列化后的字符串转换成二进制数据，因为post请求携带的是二进制参数
    last_data = bytes(data_string, 'utf8')
    res = urllib.request.urlopen(url, data=last_data)
    content = res.read()
    # 缓存起来,7200秒（两小时）有效
    return content


# 修改上传文件名称及存储路径
def get_upload_to(instance, filename):
    ext = filename.split('.')[-1]  # 获取后缀名
    filename = "%s_%d.%s" % ((datetime.datetime.now().strftime(
        '%Y%m%d%H%M%S')), random.randrange(100, 999), ext)
    return 'battle/upload/{0}_{1}'.format(instance.user.id, filename)
