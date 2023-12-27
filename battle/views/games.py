from rest_framework import viewsets, permissions, status, exceptions
from pymysql import NULL
from rest_framework.decorators import action
from rest_framework.response import Response
from battle.serializers import GamesSerializer, AccountRecordSerializer
from battle.models import Clubs, UsersClubs, Games, GameMembers, Account, ClubAccount, AccountRecord
from datetime import datetime
from math import ceil


class GamesViewSet(viewsets.ModelViewSet):
    queryset = Games.objects.all()
    serializer_class = GamesSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status']
    # 对特定字段进行排序,指定排序的字段
    ordering_fields = ['id']

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
            return Response({'isMember': True, **serializer.data}, status.HTTP_200_OK)
        else:
            # 非队员
            usefields = ['id', 'title', 'game_date', 'start_time', 'end_time',
                         'site', 'min_people', 'max_people', 'brief', 'battle', 'club', 'clubName', 'tag']
            resData = {'isMember': False}
            for field_name in serializer.data:
                if field_name in usefields:
                    resData[field_name] = serializer.data[field_name]
            return Response(resData, status.HTTP_200_OK)

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

    def destroy(self, request, *args, **kwargs):
        # 删除
        instance = self.get_object()
        user = self.request.user
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club).first()
        if user_blub and user_blub.role in [1, 2]:
            if instance.status == 2:
                return Response({'msg': '比赛已结束，不能删除'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            else:
                instance.delete()
                return Response({'msg': '删除成功'}, status=status.HTTP_200_OK)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})

    def perform_update(self, serializer):
        # 编辑
        user = self.request.user
        gameStatus = self.request.data.get('status')
        instance = self.get_object()
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club).first()

        if user_blub and user_blub.role in [1, 2] and gameStatus == instance.status:
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
        gameId = request.data.get('gameId')
        battleId = request.data.get('battleId')
        active = request.data.get('active')

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

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def settlement(self, request, *args, **kwargs):
        # 结算
        user = self.request.user
        gameId = request.data.get('gameId')
        instance = self.get_queryset().get(id=gameId)
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club.id).first()
        if user_blub and user_blub.role in [1, 2]:
            gameMembersInstance = GameMembers.objects.all().filter(
                game=gameId, club=instance.club.id)
            # 有效结算人数 ---》 剔除接替者
            activeMembers = gameMembersInstance if instance.max_people == 0 else gameMembersInstance[
                0:instance.max_people]

            gameMembersIds = list(i.user.id for i in activeMembers)
            # 去重
            gameMembersIds = list(set(gameMembersIds))

            if instance.original_price == 0 and instance.cost == 0:
                return Response({'msg': '场租原价或费用不能为空'}, status.HTTP_403_FORBIDDEN)
            if not instance.playground and instance.price:
                return Response({'msg': '选择球场才能使用优惠价结算'}, status.HTTP_403_FORBIDDEN)

            if len(gameMembersIds) >= 5:
                # 设置球队荣誉
                if instance.status == 0:
                    instance.club.honor += len(activeMembers)
                    instance.club.save()

                # 设置个人荣誉
                for member in activeMembers.filter(user__in=gameMembersIds, remarks=None):
                    if instance.status == 0:
                        member.user.honor += 1
                        member.user.save()

            # 结算球队===============>
            clubAccount = ClubAccount.objects.all().filter(
                club=instance.club.id, playground=instance.playground.id).first()
            clubAccountRecord = AccountRecord.objects.all().filter(user=None, club=instance.club.id,
                                                                   playground=instance.playground.id, game=gameId).first()

            if  clubAccount and (clubAccount.balance > 0 or clubAccountRecord):
                if not instance.price and clubAccountRecord:
                    clubAccount.balance += clubAccountRecord.amount
                    clubAccount.save()
                    clubAccountRecord.delete()

                if not clubAccountRecord and instance.price:
                    # 要扣除的金额
                    clubAccountMoney = instance.price if clubAccount.balance >= instance.price else clubAccount.balance
                    # 创建消费记录
                    accountRecordSerializer = AccountRecordSerializer(
                        data={'amount': clubAccountMoney, 'amount_type': 2, 'club': instance.club.id, 'playground': instance.playground.id, 'game': gameId})
                    if accountRecordSerializer.is_valid():
                        accountRecordSerializer.save()
                        # 球队账户中扣除
                        clubAccount.balance -= clubAccountMoney
                        clubAccount.save()
                elif instance.price:
                    differ_1 = (clubAccountRecord.amount +
                                clubAccount.balance) - instance.price
                    if differ_1 == 0:
                        clubAccountRecord.amount = instance.price
                        clubAccount.balance = 0
                    if differ_1 < 0:
                        clubAccountRecord.amount = clubAccountRecord.amount + clubAccount.balance
                        clubAccount.balance = 0
                    if differ_1 > 0:
                        clubAccountRecord.amount = instance.price
                        clubAccount.balance = differ_1
                    clubAccountRecord.save()
                    clubAccount.save()

            # 结算个人
            # 去除免费的用户
            activeMembers = list(i for i in activeMembers if i.free == False)
            total_price_1 = instance.original_price + instance.cost
            total_price_2 = instance.price + instance.cost
            price_1 = ceil(total_price_1/len(activeMembers))
            price_2 = ceil(total_price_2/len(activeMembers))

            for member in activeMembers:
                userAccount = Account.objects.all().filter(
                    user=member.user.id, club=instance.club.id, playground=instance.playground.id).first()
                # 查询本次球赛的消费记录
                userAccountRecord = AccountRecord.objects.all().filter(user=member.user.id, club=instance.club.id,
                                                                       playground=instance.playground.id, game=gameId).first()

                # 设置了优惠价、有用户账户、（用户账户余额大于0或有消费记录）、不是多次报名
                if instance.price and userAccount and (userAccount.balance > 0 or userAccountRecord) and not member.remarks:

                    if not userAccountRecord:
                        accountMoney = price_2 if userAccount.balance >= price_2 else userAccount.balance
                        # 创建消费记录
                        accountRecordSerializer = AccountRecordSerializer(
                            data={'amount': accountMoney, 'amount_type': 2, 'user': member.user.id, 'club': instance.club.id, 'playground': instance.playground.id, 'game': gameId})
                        if accountRecordSerializer.is_valid():
                            accountRecordSerializer.save()

                        if userAccount.balance >= price_2:
                            member.cost = '账户扣除'+str(accountMoney)
                        else:
                            member.cost = '账户扣除' + \
                                str(accountMoney)+'元，实付' + \
                                str(price_2-userAccount.balance)
                        userAccount.balance -= accountMoney
                        userAccount.save()
                    else:
                        # 有消费记录
                        # 消费记录与结算金额的差值
                        differ = (userAccountRecord.amount +
                                  userAccount.balance) - price_2
                        if differ == 0:
                            userAccountRecord.amount = price_2
                            userAccount.balance = 0
                            member.cost = '账户扣除' + \
                                str(price_2)
                        if differ < 0:
                            userAccountRecord.amount = userAccountRecord.amount + userAccount.balance
                            userAccount.balance = 0
                            member.cost = '账户扣除' + \
                                str(userAccountRecord.amount + userAccount.balance)+'元，实付' + \
                                str(abs(differ))
                        if differ > 0:
                            userAccountRecord.amount = price_2
                            userAccount.balance = differ
                            member.cost = '账户扣除' + \
                                str(price_2)

                        userAccountRecord.save()
                        userAccount.save()
                elif not instance.price and userAccountRecord:
                    userAccount.balance += userAccountRecord.amount
                    userAccount.save()
                    userAccountRecord.delete()
                    member.cost = price_1
                else:
                    member.cost = price_1
                member.save()
            instance.status = 1
            instance.save()
            return Response({'msg': 'ok'}, status.HTTP_200_OK)
