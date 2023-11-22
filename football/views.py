from distutils.log import error
from django.db.models import Q
from django.core.cache import cache
from pymysql import NULL
from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from football.serializers import UsersSerializer, ClubsSerializer, ClubsDetailsSerializer, UploadImagesSerializer
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
        user = request.user
        instance = self.get_object()
        serializer = ClubsDetailsSerializer(instance)
        user_blub = instance.users_clubs_set.all().values().filter(
            user_id=user.id, club_id=instance.id).first()
        source = serializer.data
        if not user.id or not user_blub:
            # 未注册和非会员，删除相应数据
            del source['members']
            # 标记非会员
            source['notJoin'] = True

        return Response(source)

    def perform_create(self, serializer):
        # 创建
        user = self.request.user
        if serializer.is_valid():
            club = serializer.save(creator=user)
            # 为创建者设置超级管理员角色
            club.members.add(user, through_defaults={'role': 1})
            print(club)
            return Response({'msg': '创建成功'}, status.HTTP_200_OK)

    def perform_destroy(self, instance):
        # 删除
        user = self.request.user
        if instance.creator == user:
            # 只有创建者才可以删除
            instance.delete()
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})

    def perform_update(self, serializer):
        # 编辑
        user = self.request.user
        instance = self.get_object()
        # 通过club的实例instance来查找中间表（UsersClubs）数据
        user_blub = instance.users_clubs_set.all().values().filter(
            user_id=user.id, club_id=instance.id).first()
        if not user_blub:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '记录不存在'})
        if user_blub.get('role') == 1:
            # 只有超级管理员可以修改
            serializer.save(data=self.request.data)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    @action(methods=['POST'], detail=False, permission_classes=[])
    def join(self, request, *args, **kwargs):
        # 直接加入
        clubId = request.data.get('id')
        user = request.user
        instance = self.get_queryset().get(id=clubId)
        if not user.id:
            return Response({'msg': '您还未登录', }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        if instance.need_apply:
            return Response({'msg': '非法操作', }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        user_blub = instance.users_clubs_set.all().values().filter(
            user_id=user.id, club_id=clubId).first()
        if not user_blub:
            instance.members.add(user, through_defaults={'role': 3})
            return Response({'msg': '加入成功'}, status.HTTP_200_OK)
        else:
            return Response({'msg': '你已经是成员了'}, status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, permission_classes=[])
    def remove(self, request, *args, **kwargs):
        # 移出
        clubId = request.data.get('id')
        userId = request.data.get('member')
        user = request.user
        instance = self.get_queryset().get(id=clubId)

        if not user.id:
            return Response({'msg': '您还未登录', }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            user_blub = instance.users_clubs_set.all().values().filter(
                user_id=user.id, club_id=clubId).first()
            if user_blub.get('role') == 1:
                instance.members.remove(userId)
                return Response({'msg': '移出成功'}, status.HTTP_200_OK)
            else:
                raise exceptions.AuthenticationFailed(
                    {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})


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
