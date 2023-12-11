from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from battle.serializers import ClubsSerializer
from battle.models import Clubs, UsersClubs


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

    def perform_create(self, serializer):
        # 创建
        user = self.request.user
        if serializer.is_valid():
            club = serializer.save(creator=user)
            # 为创建者设置超级管理员角色
            club.members.add(user, through_defaults={'role': 1})
            return Response({'msg': '创建成功'}, status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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
        if instance.creator.id == user.id:
            # 只有创建者可以修改
            serializer.save()
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def myClubs(self, request, *args, **kwargs):
        user = request.user
        # 从中间表中查对应的数据
        user_blub = UsersClubs.objects.all().filter(
            user_id=user.id)
        clubsIds = list(i.club_id for i in user_blub)
        queryset = self.filter_queryset(
            self.get_queryset()).filter(id__in=clubsIds)
        serializer = self.get_serializer(queryset, many=True)
        result = []
        for i in serializer.data:
            # 获取用户的角色
            i['role'] = user_blub.get(club_id=i['id']).role
            result.append(i)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
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

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def remove(self, request, *args, **kwargs):
        # 移出
        clubId = request.data.get('club')
        userId = request.data.get('member')
        user = request.user

        if not clubId:
            return Response({'msg': '球队ID不能为空'}, status.HTTP_503_SERVICE_UNAVAILABLE)
        if not userId:
            return Response({'msg': '用户ID不能为空'}, status.HTTP_503_SERVICE_UNAVAILABLE)

        instance = self.get_queryset().get(id=clubId)
        user_blub = instance.users_clubs_set.all().values().filter(
            user_id=user.id, club_id=clubId).first()
        # print(user.id)
        print(user_blub)
        print(str(user.id) == userId)
        if (str(user.id) == userId or (user_blub and user_blub.get('role') in [1, 2])) and str(instance.creator.id) != userId:
            instance.members.remove(userId)
            return Response({'msg': '移出成功'}, status.HTTP_200_OK)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})
