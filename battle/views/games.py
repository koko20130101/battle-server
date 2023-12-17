from rest_framework import viewsets, permissions, status, exceptions
from pymysql import NULL
from rest_framework.decorators import action
from rest_framework.response import Response
from battle.serializers import GamesSerializer
from battle.models import Clubs, UsersClubs, Games
from datetime import datetime


class GamesViewSet(viewsets.ModelViewSet):
    queryset = Games.objects.all()
    serializer_class = GamesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        user_club = UsersClubs.objects.filter(user_id=user.id)
        if user_club:
            # 查询用户所属球队的比赛
            clubsIds = list(i.club_id for i in user_club)
            queryset = self.filter_queryset(
                self.get_queryset()).filter(club__in=clubsIds)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
            else:
                serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response([], status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        # 详情
        user = request.user
        instance = self.get_object()
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club).first()
        serializer = self.get_serializer(instance)
        if user_blub:
            # 队员
            return Response({'isMember':True,**serializer.data},status.HTTP_200_OK)
        else:
            # 非队员
            usefields = ['id', 'title', 'game_date', 'start_time', 'end_time',
                     'site', 'min_people','max_people', 'brief', 'battle', 'club','clubName','tag']
            resData={'isMember':False}
            for field_name in serializer.data:
                if field_name in usefields:
                    resData[field_name] = serializer.data[field_name]
                    print(88)
            return Response(resData,status.HTTP_200_OK)
            

    def perform_create(self, serializer):
        # 创建
        user = self.request.user
        clubId = self.request.data.get('clubId')

        if not clubId:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '球队ID不能为空'})

        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=clubId).first()
        if user_blub and user_blub.role in [1, 2]:
            # 只有超级管理员和管理员才能发布比赛
            club = Clubs.objects.filter(id=clubId).first()
            serializer.save(club=club)
            return Response({'msg': '创建成功'}, status.HTTP_200_OK)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def perform_destroy(self, instance):
        # 删除
        user = self.request.user
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club).first()
        if user_blub and user_blub.role in [1, 2]:
            instance.delete()
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})

    def perform_update(self, serializer):
        # 编辑
        user = self.request.user
        instance = self.get_object()
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club).first()

        if user_blub and user_blub.role in [1, 2]:
            serializer.save()
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})

    @action(methods=['POST'], detail=False, permission_classes=[])
    def openGames(self, request, *args, **kwargs):
        # 公开的比赛
        queryset = self.filter_queryset(
            self.get_queryset()).filter(open_battle=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def battle(self, request, *args, **kwargs):
        # 应战
        user = self.request.user
        gameId = self.request.data.get('gameId')
        battleId = self.request.data.get('battleId')
        active = self.request.data.get('active')

        game_instance = self.get_queryset().get(id=gameId)
        battle_instance = self.get_queryset().get(id=battleId)
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=game_instance.club).first()
        if game_instance.club == battle_instance.club:
            return Response({'msg': '同一支球队不能应战'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if battle_instance.battle and active == '1':
            return Response({'msg': '已经被其它球队应战，请选其它比赛'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if user_blub and user_blub.role in [1, 2]:
            # 只有管理员才能应战
            game_instance.battle = battle_instance if active == '1' else None
            game_instance.save()
            battle_instance.battle = game_instance if active == '1' else None
            battle_instance.save()
            return Response({'msg': 'ok'}, status.HTTP_200_OK)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})
