from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.response import Response
from battle.serializers import GameMembersSerializer,UsersHonorSerializer
from battle.models import UsersClubs, Games, GameMembers,UsersHonor
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
        remarks = request.data.get('remarks')
        serializer = self.get_serializer(data=request.data)
        if not gameId:
            return Response({'msg': '比赛ID不能为空'}, status.HTTP_403_FORBIDDEN)
        if not clubId:
            return Response({'msg': '球队ID不能为空'}, status.HTTP_403_FORBIDDEN)

        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=clubId).first()
        game = Games.objects.get(id=gameId)

        if user_blub and game.club.id == user_blub.club_id:
            queryset = self.filter_queryset(
                self.get_queryset()).filter(game=gameId, user=user.id).first()

            if queryset and not remarks:
                return Response({'msg': '多次报名请备注'}, status.HTTP_403_FORBIDDEN)
            if game.start_time:
                if datetime.now().timestamp() > game.start_time.timestamp():
                    return Response({'msg': '超过比赛开始时间，不能报名'}, status.HTTP_403_FORBIDDEN)

            if serializer.is_valid():
                serializer.save(club=game.club)
                serializer.save(game=game)
                serializer.save(user=user)
                return Response({'msg': '报名成功'}, status.HTTP_201_CREATED)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def perform_update(self, serializer):
        # 修改参赛人员信息
        user = self.request.user
        goal = self.request.data.get('goal')
        mvp = self.request.data.get('mvp')
        instance = self.get_object()
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club.id).first()
        dif = goal - instance.goal
        if user_blub and user_blub.role in [1, 2]:
            userHonor = UsersHonor.objects.filter(user=instance.user,club=instance.club).first()
            if not userHonor:
                # 创建荣誉
                userHonor = UsersHonorSerializer(
                                data={'user': instance.user.id, 'club': user_blub.club.id, 'honor': 0,'goal':0,'mvp':0})
                if userHonor.is_valid():
                    userHonor.save()
            if type(goal)== int:
                userHonor.goal += dif
                userHonor.save()
            if mvp == True and mvp != instance.mvp:
                userHonor.mvp += 1
                userHonor.save()
            if mvp == False and mvp != instance.mvp and userHonor.mvp > 0:
                userHonor.mvp -= 1
                userHonor.save()
                

            serializer.save()
        else:
            Response({'msg': '非法操作'}, status.HTTP_503_SERVICE_UNAVAILABLE)

    def destroy(self, request, *args, **kwargs):
        # 退出比赛
        user = request.user
        instance = self.get_object()
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club).first()

        if user_blub:
            userHonor = UsersHonor.objects.filter(user=instance.user,club=instance.club).first()
            if instance.game.status == 1:
                return Response({'msg': '比赛已结束，不能取消'}, status.HTTP_403_FORBIDDEN)
            if user_blub.role in [1, 2]:
                if userHonor:
                    userHonor.mvp -= 1 if instance.mvp else 0
                    userHonor.goal -= instance.goal
                    userHonor.save()
                instance.delete()
                return Response({'msg': '取消成功'}, status.HTTP_204_NO_CONTENT)
            if instance.user == user:
                if instance.game.start_time:
                    if datetime.now().timestamp() > (instance.game.start_time - timedelta(hours=instance.game.cancel_time)).timestamp():
                        return Response({'msg': '超过取消时间，请联系管理员'}, status.HTTP_403_FORBIDDEN)
                    else:
                        if userHonor:
                            userHonor.mvp -= 1 if instance.mvp else 0
                            userHonor.goal -= instance.goal
                            userHonor.save()
                        instance.delete()
                        return Response({'msg': '取消成功'}, status.HTTP_204_NO_CONTENT)
                else:
                    if userHonor:
                        userHonor.mvp -= 1 if instance.mvp else 0
                        userHonor.goal -= instance.goal
                        userHonor.save()
                    instance.delete()
                    return Response({'msg': '取消成功'}, status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})
