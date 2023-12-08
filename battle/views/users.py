from rest_framework import viewsets, status, permissions, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from battle.serializers import UsersSerializer
from battle.models import Users
from battle.permissions import IsOwner
from config.settings import APP_ID, SECRET
from common.utils import getSessionInfo


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

    def update(self, request, *args, **kwargs):
        # 不能put更新
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def retrieve(self, request, *args, **kwargs):
        # 不能get查看用户信息
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
            }, status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    # 注册
    @action(methods=['POST'], detail=False, permission_classes=[])
    def register(self, request, *args, **kwargs):
        jsCode = request.data.get('jsCode')
        nickName = request.data.get('nickName')
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
                    data={'open_id': openId, 'username': openId, 'password': '123456',  'nick_name': nickName})
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
            return Response({'msg': 'jsCode不能为空'}, status.HTTP_503_SERVICE_UNAVAILABLE)

    # 用户信息
    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated, IsOwner])
    def getUserInfo(self, request, *args, **kwargs):
        instance = self.filter_queryset(
            self.get_queryset()).filter(id=request.user.id).first()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response({
                'msg': '您还未注册',
            }, status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    # 设置信息
    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated, IsOwner])
    def setUserInfo(self, request, *args, **kwargs):
        instance = self.filter_queryset(
            self.get_queryset()).filter(id=request.user.id).first()
        if instance:
            instance.nick_name = request.data.get('nick_name')
            instance.avatar = request.data.get('avatar')
            instance.save()
            return Response({'msg': '修改成功'}, status.HTTP_200_OK)
        else:
            return Response({
                'msg': '您还未注册',
            }, status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)
