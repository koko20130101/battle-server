from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.response import Response
from battle.serializers import GameMembersSerializer
from battle.models import UsersClubs, Games, GameMembers
from config.settings import APP_ID, SECRET
from datetime import datetime,timedelta


class GameMembersViewSet(viewsets.ModelViewSet):
    '''参赛人员视图集'''
    queryset = GameMembers.objects.all()
    serializer_class = GameMembersSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        clubId = request.GET.get('clubId')
        gameId = request.GET.get('gameId')
        user_club = UsersClubs.objects.filter(
            user_id=user.id, club_id=clubId).first()
        if user_club:
            queryset = self.filter_queryset(
                self.get_queryset()).filter(game=gameId, club=clubId)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
           return Response([], status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def perform_create(self, serializer):
        # 申请比赛
        user = self.request.user
        clubId = self.request.data.get('clubId')
        gameId = self.request.data.get('gameId')
        if not gameId:
            return Response({'msg': '比赛ID不能为空'}, status.HTTP_403_FORBIDDEN)
        if not clubId:
            return Response({'msg': '球队ID不能为空'}, status.HTTP_403_FORBIDDEN)

        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=clubId).first()
        game = Games.objects.get(id=gameId)

        if user_blub and game.club.id == user_blub.club_id:
            serializer.save(club=game.club)
            serializer.save(game=game)
            serializer.save(user=user)
            return Response({'msg': '创建成功'}, status.HTTP_200_OK)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def perform_destroy(self, instance):
        # 退出比赛
        user = self.request.user
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club).first()

        if user_blub:
            if  instance.user == user or user_blub.role in [1,2]:
                if instance.game.start_time:
                    # print(timedelta(hours=1))
                    print(instance.game.start_time)
                    # print((datetime(instance.game.end_time) + timedelta(hours=1)).timestamp())
                    # print((datetime(instance.game.end_time) + timedelta(hours=1)).timestamp())
                    # instance.delete()
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})
