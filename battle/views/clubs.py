from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from battle.serializers import ClubsSerializer
from battle.models import Clubs, UsersClubs, Apply


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
        # 详情
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        user = request.user
        result = {}
        if user:
            # 从中间表中查对应的数据
            user_blub = UsersClubs.objects.all().filter(club_id=instance.id,
                                                        user_id=user.id).first()
            if user_blub:
                if user_blub.role in [1, 2]:
                    # 超级管理员和管理员显示申请人数
                    apply = Apply.objects.all().filter(
                        club_id=instance.id)
                    # 申请人数
                    result['applyTotal'] = len(apply)
                # 角色
                result['role'] = user_blub.role
        return Response({**result, **serializer.data})

    def destroy(self, request, *args, **kwargs):
        # 删除
        instance = self.get_object()
        user = self.request.user
        if instance.creator == user:
            # 只有创建者才可以删除
            if len(instance.members.values()) > 1:
                return Response({'msg': '请先手动删除其它成员才能解散球队！'},
                                status.HTTP_403_FORBIDDEN)
            else:
                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})

    def perform_update(self, serializer):
        # 编辑
        user = self.request.user
        honor = self.request.data.get('honor')
        game_total = self.request.data.get('game_total')
        instance = self.get_object()
        if instance.creator.id == user.id and not honor and not game_total:
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
            i['role'] = user_blub.filter(club_id=i['id']).first().role
            if i['role'] in [1, 2]:
                apply = Apply.objects.all().filter(
                    club_id=i['id'])
                i['applyTotal'] = len(apply)
            result.append(i)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def join(self, request, *args, **kwargs):
        # 申请加入
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
        clubId = request.data.get('clubId')
        memberId = request.data.get('memberId')
        user = request.user

        if not clubId:
            return Response({'msg': '球队ID不能为空'}, status.HTTP_503_SERVICE_UNAVAILABLE)

        instance = self.get_queryset().get(id=clubId)

        if not memberId and instance.creator.id != user.id:
            # 没有传memberId,且该用户不是队长，则自己退出
            instance.members.remove(user.id)
            return Response({'msg': '操作成功'}, status.HTTP_200_OK)

        user_blub = instance.users_clubs_set.all(
        ).filter(user_id=user.id, club_id=clubId).first()
        if memberId and user_blub.role in [1, 2]:
            # 查询出要称除的成员
            memberQueryset = instance.users_clubs_set.all(
            ).filter(id=memberId, club_id=clubId).first()
            print(instance.creator.id == user.id)

            if memberQueryset.role == 1:
                return Response({'msg': '非法操作'}, status.HTTP_403_FORBIDDEN)
            else:
                instance.members.remove(memberQueryset.user_id)
                return Response({'msg': '操作成功'}, status.HTTP_200_OK)

        return Response({'msg': '非法操作'}, status.HTTP_403_FORBIDDEN)

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def setClubAdmin(self, request, *args, **kwargs):
        # 设置或取消管理员
        clubId = request.data.get('clubId')
        memberId = request.data.get('memberId')
        user = request.user

        if not clubId:
            return Response({'msg': '球队ID不能为空'}, status.HTTP_503_SERVICE_UNAVAILABLE)
        if not memberId:
            return Response({'msg': '队员ID不能为空'}, status.HTTP_503_SERVICE_UNAVAILABLE)

        instance = self.get_queryset().get(id=clubId)
        user_blub = instance.users_clubs_set.all().values().filter(
            user_id=user.id, club_id=clubId).first()
        # print(user.id)

        if user_blub and user_blub.get('role') == 1 and str(instance.creator.id) != user.id:
            user_blub = instance.users_clubs_set.all().filter(
                id=memberId, club_id=clubId).first()
            user_blub.role = 2 if user_blub.role == 3 else 3
            user_blub.save()
            return Response({'msg': '操作成功'}, status.HTTP_200_OK)
        else:
            return Response({'msg': '非法操作'}, status.HTTP_403_FORBIDDEN)
