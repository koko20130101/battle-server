from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from battle.serializers import BattleApplySerializer
from battle.models import BattleApply, Games, GameMembers, UsersClubs


class BattleApplyViewSet(viewsets.ModelViewSet):
    queryset = BattleApply.objects.all()
    serializer_class = BattleApplySerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # 申请列表
        user = request.user
        gameId = request.GET.get('gameId')

        if not gameId:
            return Response({'msg': '比赛ID不能为空'}, status.HTTP_503_SERVICE_UNAVAILABLE)
        instance = self.filter_queryset(
            self.get_queryset()).filter(game=gameId).first()
        if instance:
            user_blub = UsersClubs.objects.filter(
                user_id=user.id, club_id=instance.game.club.id).first()
            # 验证用户
            if user_blub and user_blub.role in [1, 2]:
                queryset = self.filter_queryset(
                    self.get_queryset()).filter(game=gameId)
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                else:
                    serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
            else:
                return Response({'msg': '您无权操作'}, status.HTTP_403_FORBIDDEN)
        return Response([])

    def create(self, request, *args, **kwargs):
        # 申请
        user = request.user
        gameId = request.data.get('gameId')
        battleId = request.data.get('battleId')
        remarks = request.data.get('remarks')

        if not gameId:
            return Response({'msg': 'gameId不能为空'}, status.HTTP_503_SERVICE_UNAVAILABLE)
        if not battleId:
            return Response({'msg': '应战队伍不能为空'}, status.HTTP_503_SERVICE_UNAVAILABLE)

        game = Games.objects.get(id=gameId)
        battle = Games.objects.get(id=battleId)

        if game.club == battle.club:
            return Response({'msg': '相同球队不能应战'}, status.HTTP_503_SERVICE_UNAVAILABLE)

        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=battle.club).first()

        if user_blub and user_blub.role in [1, 2]:
            game_members = GameMembers.objects.filter(game=gameId)
            game_members_ids = list(set(list(i.user.id for i in game_members)))

            if len(game_members_ids) < game.competition:
                return Response({'msg': f'''您的队伍最少要{game.competition}个不同用户报名'''}, status.HTTP_503_SERVICE_UNAVAILABLE)

            apply = self.get_queryset().filter(
                game=gameId, rival=battleId).first()
            if apply:
                apply.remarks = remarks
                apply.save()
                return Response({'msg': '您已提交过，请等待对方确认'}, status.HTTP_503_SERVICE_UNAVAILABLE)

            applyData = {
                'game': gameId,
                'rival': battleId,
                'remarks': remarks
            }
            serializer = self.get_serializer(data=applyData)
            if serializer.is_valid():
                # serializer.save()
                return Response({'msg': '提交成功，请等待对方确认'}, status.HTTP_200_OK)
        else:
            return Response({'msg': '您无权操作'}, status.HTTP_403_FORBIDDEN)

    def perform_update(self, instance):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})

    def perform_destroy(self, instance):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def agree(self, request, *args, **kwargs):
        # 同意
        user = request.user
        applyId = request.data.get('applyId')

        if not applyId:
            return Response({'msg': '申请ID不能为空'}, status.HTTP_503_SERVICE_UNAVAILABLE)

        apply = self.get_queryset().filter(id=applyId).first()
        if apply:
            user_blub = UsersClubs.objects.filter(
                user_id=user.id, club_id=apply.game.club.id).first()

            if user_blub and user_blub.role in [1, 2]:
                apply.game.battle = apply.rival
                apply.rival.battle = apply.game
                apply.game.save()
                apply.rival.save()
                apply.delete()

                return Response({'msg': 'ok'}, status.HTTP_200_OK)
            else:
                raise exceptions.AuthenticationFailed(
                    {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})
