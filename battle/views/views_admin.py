from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from battle.serializers import AdvertSerializer, UploadImagesSerializer, MessageSerializer, UsersSerializer, ClubsSerializer
from battle.models import UploadImages, Message, Advert, Users, Clubs
from battle.permissions import IsSuperUser
import datetime
# django自带的验证机制
from django.contrib.auth import authenticate, login, logout  # 验证、登入、登出


class AdminUsersViewSet(viewsets.ModelViewSet):
    '''用户视图集'''
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    # 指定可以过滤字段
    filterset_fields = ['real_name', 'nick_name', 'created']
    # 对特定字段进行排序,指定排序的字段
    # ordering_fields = ['id', 'rank']

    # 登录
    @action(methods=['POST'], detail=False, permission_classes=[])
    def login(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'status': status.HTTP_503_SERVICE_UNAVAILABLE,
                'msg': '用户名或密码不能为空',
            })
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            serializer = self.get_serializer(user)
            return Response({
                'status': status.HTTP_200_OK,
                'msg': '登录成功',
                'data': dict(serializer.data, **{'userName': username})
            })
        else:
            return Response({
                'status': status.HTTP_503_SERVICE_UNAVAILABLE,
                'msg': '用户不存在或用户密码输入错误!!',
            })

    # 登出
    @action(methods=['GET'], detail=False, permission_classes=[])
    def logout(self, request, *args, **kwargs):
        try:
            logout(request)
            return Response({
                'status': status.HTTP_200_OK,
                'msg': '登出成功',
            })
        except:
            return Response({
                'status': status.HTTP_503_SERVICE_UNAVAILABLE,
                'msg': '服务调用失败',
            })

    # 修改密码
    @action(methods=['POST'], detail=False)
    def updatePassword(self, request, *args, **kwargs):
        oldPassword = request.data.get('oldPassword')
        newPassword = request.data.get('newPassword')
        try:
            user = request.user
            if user.check_password(oldPassword):  # 判断前端传过来的密码是否正确，如果正确，返回一个值
                user.set_password(newPassword)  # 把前端输入的新密码加密放进数据库里面
                user.save()
                # 更新session，因为原来的session存放的是旧密码
                # update_session_auth_hash(request, user)
            else:
                return Response({'status': status.HTTP_503_SERVICE_UNAVAILABLE, 'msg': '旧密码错误'})
        except Exception as e:
            return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'msg': '服务器异常'})
        return Response({'status': status.HTTP_200_OK, 'msg': '修改密码成功'})


class AdminAdvertViewSet(viewsets.ModelViewSet):
    '''广告位'''
    queryset = Advert.objects.all()
    serializer_class = AdvertSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    # 指定可以过滤字段
    filterset_fields = ['title', 'ad_type']


class ImageUploadViewSet(viewsets.ModelViewSet):
    '''上传图片视图集'''
    queryset = UploadImages.objects.all()
    serializer_class = UploadImagesSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


class AdminMessageViewSet(viewsets.ModelViewSet):
    '''消息管理'''
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    # 指定可以过滤字段
    filterset_fields = ['message', 'm_type']

    def perform_update(self, serializer):
        serializer.save(reply_time=datetime.datetime.now())


class AdminClubsViewSet(viewsets.ModelViewSet):
    '''球队管理'''
    queryset = Clubs.objects.all()
    serializer_class = ClubsSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    # 指定可以过滤字段
    filterset_fields = ['club_name', 'hot']

    def create(self, request, *args, **kwargs):
        return Response({'msg': '无权操作'},
                        status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        return Response({'msg': '无权操作'},
                        status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        return Response({'msg': '无权操作'},
                        status.HTTP_403_FORBIDDEN)

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated, IsSuperUser])
    def setHot(self, request, *args, **kwargs):
        # 设置热门
        id = request.data.get('id')
        hot = request.data.get('hot')
        instance = self.filter_queryset(
            self.get_queryset()).filter(id=id).first()
        if instance:
            instance.hot = hot
            instance.save()
            return Response({'msg': 'ok'}, status.HTTP_200_OK)
