from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.response import Response
from rest_framework.decorators import action
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

        user_cblub = UsersClubs.objects.filter(
            user_id=user.id, club_id=clubId).first()
        game = Games.objects.get(id=gameId)
        print(user_cblub.group)
        if user_cblub and game.club.id == user_cblub.club_id:
            queryset = self.filter_queryset(
                self.get_queryset()).filter(game=gameId, user=user.id,remarks='').first()

            if queryset and not remarks:
                return Response({'msg': '多次报名请备注'}, status.HTTP_403_FORBIDDEN)
            if game.start_time:
                if datetime.now().timestamp() > game.start_time.timestamp():
                    return Response({'msg': '超过比赛开始时间，不能报名'}, status.HTTP_403_FORBIDDEN)

            if serializer.is_valid():
                serializer.save(club=game.club)
                serializer.save(game=game)
                # 2024-7-14 取消自动分组
                # serializer.save(group=user_cblub.group)
                serializer.save(user=user)
                return Response({'msg': '报名成功'}, status.HTTP_201_CREATED)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def update(self, request, *args, **kwargs):
        # 修改参赛人员信息
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        user = request.user
        goal = request.data.get('goal')
        assist = request.data.get('assist')
        mvp = request.data.get('mvp')

        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club.id).first()
        dif = goal - instance.goal
        difAssist = assist - instance.assist
        difMvp = mvp - instance.mvp
        # 管理员和球员自己可以设置进球
        if user_blub and (user_blub.role in [1, 2] or user == instance.user):
            # 查寻当月的荣誉记录
            userHonor = UsersHonor.objects.filter(user=instance.user,club=instance.club,year=datetime.now().strftime('%Y'),month=datetime.now().strftime('%m')).first()
            if not userHonor and not instance.remarks:
                # 创建荣誉
                userHonorSerializer = UsersHonorSerializer(
                                data={'user': instance.user.id, 'club': user_blub.club.id, 'honor': 0,'goal':0,'assist':0,'mvp':0,"year":datetime.now().strftime('%Y'),"month":datetime.now().strftime('%m')})
                if userHonorSerializer.is_valid():
                    userHonor = userHonorSerializer.save()
            canSet = True if (instance.game.start_time and datetime.now().timestamp() > instance.game.start_time.timestamp()) else False
            if (dif != 0 or difAssist != 0 or difMvp != 0 ) and not canSet:
                return Response({'msg': '还未到开赛时间'}, status.HTTP_403_FORBIDDEN)
            if datetime.now().timestamp() > (instance.game.end_time + timedelta(hours=48)).timestamp():
                return Response({'msg': '比赛已结束两天，不能再设置'}, status.HTTP_403_FORBIDDEN)
            if not instance.remarks:
                if type(goal) == int:
                    if instance.game.game_type == 1:
                        # 内战进球
                        userHonor.goal += dif
                    if instance.game.game_type == 2:
                        # 外战进球
                        userHonor.goal_out += dif
                    userHonor.save()
                if type(assist) == int:
                    if instance.game.game_type == 1:
                        # 内战助攻
                        userHonor.assist += difAssist
                    if instance.game.game_type == 2:
                        # 外战助攻
                        userHonor.assist_out += difAssist
                    userHonor.save()
                # mvp不能大于1
                if type(mvp) == int and user_blub.role in [1, 2] and mvp < 2:
                    userHonor.mvp += difMvp
                    userHonor.save()
                
            if serializer.is_valid():
                serializer.save()
            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            return Response({'msg': 'OK'}, status.HTTP_200_OK)
        else:
            return Response({'msg': '非法操作'}, status.HTTP_503_SERVICE_UNAVAILABLE)

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
                if userHonor and not instance.remarks:
                    userHonor.assist -= userHonor.assist
                    userHonor.goal -= instance.goal
                    userHonor.save()
                instance.delete()
                return Response({'msg': '取消成功'}, status.HTTP_204_NO_CONTENT)
            if instance.user == user:
                if instance.game.start_time:
                    if datetime.now().timestamp() > (instance.game.start_time - timedelta(hours=instance.game.cancel_time)).timestamp():
                        return Response({'msg': '超过取消时间，请联系管理员'}, status.HTTP_403_FORBIDDEN)
                    else:
                        if userHonor and not instance.remarks:
                            userHonor.assist -= instance.assist
                            userHonor.goal -= instance.goal
                            userHonor.save()
                        instance.delete()
                        return Response({'msg': '取消成功'}, status.HTTP_204_NO_CONTENT)
                else:
                    if userHonor and not instance.remarks:
                        userHonor.assist -= userHonor.assist
                        userHonor.goal -= instance.goal
                        userHonor.save()
                    instance.delete()
                    return Response({'msg': '取消成功'}, status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    @action(methods=['POST'], detail=False, permission_classes=[])
    def joinGroup(self, request, *args, **kwargs):
        # 加入分组
        user = request.user
        id = request.data.get('id')
        group = request.data.get('group')
        member_instance = self.filter_queryset(self.get_queryset()).filter(id=id).first()
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=member_instance.club).first()
        # if user_blub and ( user_blub.role in [1, 2] or user == member_instance.user):
        if user_blub and user_blub.role in [1, 2]:
                member_instance.group = group
                member_instance.save()
                return Response({'msg': 'ok'}, status.HTTP_200_OK)
        else:
            return Response({'msg': '非法操作'}, status.HTTP_403_FORBIDDEN)