from rest_framework import viewsets, permissions, status, exceptions
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from battle.serializers import PlaygroundsSerializer
from battle.models import Playgrounds, Clubs, UsersClubs, ClubsPlaygrounds, Account


class PlaygroundsViewSet(viewsets.ModelViewSet):
    '''球场视图集'''
    queryset = Playgrounds.objects.all()
    serializer_class = PlaygroundsSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['id']
    # 指定可以过滤字段
    filterset_fields = ['playground_name', 'area']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def perform_create(self, serializer):
        # 创建
        user = self.request.user
        if user.is_superuser:
            serializer.save()
        else:
            return Response({'msg': '非法操作'}, status.HTTP_403_FORBIDDEN)

    def perform_update(self, serializer):
        user = self.request.user
        if user.is_superuser:
            serializer.save()
        else:
            return Response({'msg': '非法操作'}, status.HTTP_403_FORBIDDEN)

    def perform_destroy(self, instance):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def clubPlaygrounds(self, request, *args, **kwargs):
        user = request.user
        clubId = request.data.get('clubId')
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=clubId).first()
        if user_blub:
            # 从中间表中查对应的数据
            clubs_playgrounds = ClubsPlaygrounds.objects.all().filter(
                club_id=clubId)

            clubsIds = list(i.playground_id for i in clubs_playgrounds)
            queryset = self.filter_queryset(
                self.get_queryset()).filter(id__in=clubsIds)
            serializer = self.get_serializer(queryset, many=True)

            result = []

            for i in serializer.data:
                # 获取用户的角色
                i['main'] = clubs_playgrounds.filter(
                    playground_id=i['id']).first().main
                result.append(i)
            return Response(result, status.HTTP_200_OK)
        else:
            return Response([], status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def addPlayground(self, request, *args, **kwargs):
        # 添加并绑定场地，或绑定场地
        user = request.user
        id = request.data.get('id')
        clubId = request.data.get('clubId')
        playground_name = request.data.get('playground_name')
        area = request.data.get('area')
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=clubId).first()
        if user_blub and user_blub.role in [1, 2]:
            playground_instance = self.filter_queryset(self.get_queryset()).filter(
                playground_name=playground_name, area=area).first()
            if playground_instance:
                if not id:
                    # 同地区，同名
                    return Response({'msg': '球场已存在，请在查询结果中选择'}, status.HTTP_403_FORBIDDEN)
                else:
                    # 绑定场地到球队
                    user_blub.club.playgrounds.add(playground_instance)
            else:
                # 新增场地
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                new_playground = serializer.save()
                # 绑定新场地到球队
                user_blub.club.playgrounds.add(new_playground)
            return Response({'msg': '添加成功'}, status.HTTP_200_OK)
        else:
            return Response({'msg': '非法操作'}, status.HTTP_403_FORBIDDEN)

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def deletePlayground(self, request, *args, **kwargs):
        # 删除绑定场地
        user = request.user
        id = request.data.get('id')
        clubId = request.data.get('clubId')
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=clubId).first()
        if user_blub and user_blub.role in [1, 2]:
            playground_instance = user_blub.club.playgrounds.filter(
                id=id).first()
            if playground_instance:
                users = UsersClubs.objects.filter(club_id=clubId)
                account = Account.objects.all().filter(user__in=list(
                    i.user for i in users), club=clubId, playground=id)
                if len(list(i.balance for i in account if i.balance > 0)):
                    return Response({'msg': '球队成员在该场地还有余额，不能删除！'}, status.HTTP_403_FORBIDDEN)
                else:
                    # 删除场地绑定关系
                    user_blub.club.playgrounds.remove(playground_instance)
            else:
                return Response({'msg': '找不到记录'}, status.HTTP_403_FORBIDDEN)
            return Response({'msg': '删除成功'}, status.HTTP_200_OK)
        else:
            return Response({'msg': '非法操作'}, status.HTTP_403_FORBIDDEN)

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def setMainPlayground(self, request, *args, **kwargs):
        # 设置主场地
        user = request.user
        id = request.data.get('id')
        clubId = request.data.get('clubId')
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=clubId).first()
        if user_blub and user_blub.role in [1, 2]:
            clubs_playgrounds = ClubsPlaygrounds.objects.all().filter(
                club_id=clubId)
            club = Clubs.objects.get(id=clubId)
            for i in clubs_playgrounds:
                print(i.playground.playground_name)
                if i.playground_id == id:
                    i.main = True
                    club.main_playground = i.playground.playground_name
                    club.save()
                else:
                    i.main = False
                i.save()
            return Response({'msg': '设置成功'}, status.HTTP_200_OK)
        else:
            return Response({'msg': '非法操作'}, status.HTTP_403_FORBIDDEN)
