from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from football.serializers import ClubsSerializer, ClubsDetailsSerializer
from football.models import Clubs


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
        if instance.creator.id == user.id:
            # 只有创建者可以修改
            serializer.save()
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

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
