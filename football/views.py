from distutils.log import error
from django.db.models import Q
from django.core.cache import cache
from pymysql import NULL
from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from football.serializers import UsersSerializer, ClubsSerializer, UploadImagesSerializer, ClubsDetailsSerializer
from football.models import Users, Clubs, UploadImages
from football.permissions import IsOwnerOrReadOnly
from config.settings import APP_ID, SECRET
from common.utils import getSessionInfo
from PIL import Image
from io import BytesIO


class UsersViewSet(viewsets.ModelViewSet):
    '''用户视图集'''
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

    def list(self, request, *args, **kwargs):
        # 不能查看用户列表
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def perform_create(self, serializer):
        # 不能创建
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    # 登录
    @action(methods=['POST'], detail=False, permission_classes=[])
    def login(self, request, *args, **kwargs):
        jsCode = request.data.get('jsCode')
        if not jsCode:
            return Response({
                'msg': 'jsCode不能为空',
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        sessionInfo = getSessionInfo(jsCode, APP_ID, SECRET)
        if not sessionInfo.get('openid'):
            return Response({'msg': 'jsCode失效'}, status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            openId = sessionInfo['openid']

        user = self.queryset.filter(open_id=openId).first()
        try:
            old_token = Token.objects.get(user=user)
            old_token.delete()
        except:
            pass
        if user:
            token = Token.objects.create(user=user)
            return Response({'token': token.key}, status.HTTP_200_OK)
        else:
            return Response({
                'msg': '您还未注册',
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    # 注册
    @action(methods=['POST'], detail=False, permission_classes=[])
    def register(self, request, *args, **kwargs):
        jsCode = request.data.get('jsCode')
        nickName = request.data.get('nickName')
        avatar = request.data.get('avatar')
        if jsCode:
            sessionInfo = getSessionInfo(jsCode, APP_ID, SECRET)

            if not sessionInfo.get('openid'):
                return Response({'msg': 'jsCode失效'}, status.HTTP_503_SERVICE_UNAVAILABLE)
            else:
                openId = sessionInfo['openid']

            user = self.queryset.filter(open_id=openId).first()
            if user:
                return Response({'msg': '注册失败，用户已存在'}, status.HTTP_503_SERVICE_UNAVAILABLE)
            else:
                serializer = UsersSerializer(
                    data={'open_id': openId, 'username': openId, 'password': '123456',  'nick_name': nickName, 'avatar': avatar})
                if serializer.is_valid():
                    user = serializer.save()
                    try:
                        old_token = Token.objects.get(user=user)
                        old_token.delete()
                    except:
                        pass
                    token = Token.objects.create(user=user)
                    return Response({'token': token.key, 'msg': '注册成功'}, status.HTTP_200_OK)
                else:
                    return Response({'msg': serializer.errors})
        else:
            return Response({'msg': 'jsCOde不能为空'}, status.HTTP_503_SERVICE_UNAVAILABLE)


class ClubsViewSet(viewsets.ModelViewSet):
    '''俱乐部视图集'''
    queryset = Clubs.objects.all()
    serializer_class = ClubsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # 对特定字段进行排序,指定排序的字段
    ordering_fields = ['id', 'honor']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        # 详情
        instance = self.get_object()
        serializer = ClubsDetailsSerializer(instance)
        return Response(serializer.data)

    def perform_destroy(self, instance):
       # 不能删除
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            club = serializer.save()
            # 为创建者设置超级管理员角色
            club.members.add(user, through_defaults={'role': 1})
            return Response({'msg': '创建成功'}, status.HTTP_200_OK)


class ImageUploadViewSet(viewsets.ModelViewSet):
    '''上传图片视图集'''
    queryset = UploadImages.objects.all()
    serializer_class = UploadImagesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
