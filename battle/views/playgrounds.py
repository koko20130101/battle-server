from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from battle.serializers import PlaygroundsSerializer
from battle.models import Playgrounds, UsersClubs, ClubsPlaygrounds


class PlaygroundsViewSet(viewsets.ModelViewSet):
    '''球场视图集'''
    queryset = Playgrounds.objects.all()
    serializer_class = PlaygroundsSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 指定可以过滤字段
    filterset_fields = ['playground_name']

    def list(self, request, *args, **kwargs):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def perform_create(self, serializer):
        # 创建
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def perform_update(self, request, *args, **kwargs):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

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
            # result = []
            # serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response({'msg': '非法操作'}, status.HTTP_403_FORBIDDEN)

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
                    return Response({'msg': '场地已存在该地区，请在查询结果中选择'}, status.HTTP_403_FORBIDDEN)
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
            playground_instance = user_blub.club.playgrounds.filter(id=id).first()
            if playground_instance:
                user_blub.club.playgrounds.remove(playground_instance)
            else:
                return Response({'msg': '找不到记录'}, status.HTTP_403_FORBIDDEN)
            return Response({'msg': '删除成功'}, status.HTTP_200_OK)
        else:
            return Response({'msg': '非法操作'}, status.HTTP_403_FORBIDDEN)