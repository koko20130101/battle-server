from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.response import Response
from battle.serializers import GameMembersSerializer
from battle.models import UsersClubs, Games, GameMembers
from config.settings import APP_ID, SECRET
from datetime import datetime, timedelta


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

    def create(self, request, *args, **kwargs):
        # 申请比赛
        user = request.user
        clubId = request.data.get('clubId')
        gameId = request.data.get('gameId')
        serializer = self.get_serializer(data=request.data)
        if not gameId:
            return Response({'msg': '比赛ID不能为空'}, status.HTTP_403_FORBIDDEN)
        if not clubId:
            return Response({'msg': '球队ID不能为空'}, status.HTTP_403_FORBIDDEN)

        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=clubId).first()
        game = Games.objects.get(id=gameId)

        if user_blub and game.club.id == user_blub.club_id:
            if game.start_time:
                if datetime.now().timestamp() > game.start_time.timestamp():
                    return Response({'msg': '超过比赛开始时间，不能报名'}, status.HTTP_403_FORBIDDEN)
            if serializer.is_valid():
                serializer.save(club=game.club)
                serializer.save(game=game)
                serializer.save(user=user)
                return Response({'msg': '创建成功'}, status.HTTP_201_CREATED)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def destroy(self, request, *args, **kwargs):
        # 退出比赛
        user = request.user
        instance = self.get_object()
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club).first()

        if user_blub:
            if user_blub.role in [1, 2]:
                instance.delete()
                return Response({'msg': '取消成功'}, status.HTTP_204_NO_CONTENT)
            if instance.user == user:
                if instance.game.start_time:
                    if datetime.now().timestamp() > (instance.game.start_time - timedelta(hours=instance.game.cancel_time)).timestamp():
                        return Response({'msg': '超过取消时间，请联系管理员'}, status.HTTP_403_FORBIDDEN)
                    else:
                        instance.delete()
                        return Response({'msg': '取消成功'}, status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})
