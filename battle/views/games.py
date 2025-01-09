from rest_framework import viewsets, permissions, status, exceptions
from pymysql import NULL
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from battle.serializers import GamesSerializer, AccountRecordSerializer,UsersHonorSerializer
from battle.models import Clubs, UsersClubs,UsersHonor, Games, GameMembers, Account, ClubAccount, AccountRecord
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
        user_club = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club).first()
        serializer = self.get_serializer(instance)
        if user_club:
            # 队员
            return Response({'isMember': True, **serializer.data}, status.HTTP_200_OK)
        else:
            # 非队员
            usefields = ['id', 'title', 'game_date', 'start_time', 'end_time', 'open_battle', 'competition',
                         'site', 'min_people', 'max_people', 'brief', 'rivalName', 'rivalLogo', 'club', 'clubLogo','clubName', 'tag']
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

        user_club = UsersClubs.objects.filter(
            user_id=user.id, club_id=clubId).first()
        if user_club and user_club.role in [1, 2]:
            # 只有超级管理员和管理员才能发布比赛
            club = Clubs.objects.filter(id=clubId).first()
            serializer.save(club=club)
            serializer.save(creator=user)
            return Response({'msg': '创建成功'}, status.HTTP_200_OK)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def destroy(self, request, *args, **kwargs):
        # 删除
        instance = self.get_object()
        user = request.user
        user_club = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club).first()
        if user_club and (user_club.role == 1 or instance.creator == user):
            if instance.status == 2:
                return Response({'msg': '比赛已结束，不能删除'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            else:
                instance.delete()
                return Response({'msg': '删除成功'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': '您无权操作'},status=status.HTTP_403_FORBIDDEN)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        user = request.user
        gameStatus = request.data.get('status')
        game_type = request.data.get('game_type')
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if gameStatus != instance.status:
            return Response({'msg': '非法操作'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        user_club = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club).first()
        
        if game_type != instance.game_type:
            gameMembersInstance = GameMembers.objects.all().filter(Q(game=instance.id,club=instance.club.id,assist__gt=0) | Q(game=instance.id,club=instance.club.id,goal__gt=0))
            if gameMembersInstance:
                return Response({'msg': '已记录比赛数据，不能修改类型'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        if user_club and user_club.role in [1, 2] and serializer.is_valid():
            serializer.save()
            return Response({'msg': 'OK','data':serializer.data}, status.HTTP_200_OK)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})

    @action(methods=['POST'], detail=False, permission_classes=[])
    def openGames(self, request, *args, **kwargs):
        # 公开的比赛
        queryset = self.filter_queryset(
            self.get_queryset()).filter(open_battle=True, status=0, start_time__gt=datetime.now())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def cancelBattle(self, request, *args, **kwargs):
        # 取消应战
        user = self.request.user
        gameId = request.data.get('gameId')
        game_instance = self.get_queryset().get(id=gameId)

        user_club = UsersClubs.objects.filter(
            user_id=user.id, club_id=game_instance.club).first()

        if user_club and user_club.role in [1, 2]:
            # 只有管理员才能操作
            # 设置对手的对手为空
            game_instance.battle.battle = None
            game_instance.battle.save()
            game_instance.battle = None
            game_instance.remarks = ''
            game_instance.save()
            return Response({'msg': 'ok'}, status.HTTP_200_OK)
        else:
            return Response({'msg': '非法操作'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def settlement(self, request, *args, **kwargs):
        # 结算
        user = self.request.user
        gameId = request.data.get('gameId')
        instance = self.get_queryset().get(id=gameId)
        user_club = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club.id).first()
        if user_club and user_club.role in [1, 2]:
            gameMembersInstance = GameMembers.objects.all().filter(
                game=gameId, club=instance.club.id)
            # 有效结算人数 ---》 剔除接替者
            activeMembers = gameMembersInstance if instance.max_people == 0 else gameMembersInstance[
                0:instance.max_people]

            # 本人参加
            gameMembersIdsOnly = list(i.user.id for i in activeMembers if i.remarks == None)
            # 有备注的ID
            gameMembersIdsHasRemarks = list(i.user.id for i in activeMembers if i.remarks != None)
            # 去重
            gameMembersIdsHasRemarksOnly = list(set(gameMembersIdsHasRemarks))

            # if instance.original_price == 0 and instance.cost == 0:
            #     return Response({'msg': '场租原价或费用不能为空'}, status.HTTP_403_FORBIDDEN)
            if not instance.playground:
                return Response({'msg': '场地不能为空'}, status.HTTP_403_FORBIDDEN)
            if len(activeMembers) == 0:
                return Response({'msg': '没有人参加的比赛不能结算'}, status.HTTP_403_FORBIDDEN)

            

            # 结算球队===============>
            clubAccount = ClubAccount.objects.all().filter(
                club=instance.club.id, playground=instance.playground.id).first()
            clubAccountRecord = AccountRecord.objects.all().filter(user=None, club=instance.club.id,
                                                                   playground=instance.playground.id, game=gameId).first()
            if clubAccount and (clubAccount.balance > 0 or clubAccountRecord):
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
            
            if len(gameMembersIdsOnly) >= 5:
                if instance.status == 0:
                    # 设置球队荣誉
                    instance.club.honor += ceil(len(activeMembers)/10)
                    if instance.battle:
                        # 设置信誉
                        instance.club.credit += 1

                # 设置个人荣誉
                for user_id in gameMembersIdsOnly:
                    if instance.status == 0:
                        userHonor = UsersHonor.objects.filter(user_id=user_id,club=instance.club,year=datetime.now().strftime('%Y'),month=datetime.now().strftime('%m')).first()
                        if userHonor:
                            userHonor.honor += 1
                            userHonor.save()
                        else:
                            # 创建记录
                            usersHonorSerializer = UsersHonorSerializer(
                                data={'user':user_id, 'club': instance.club.id, 'honor': 1,'goal':0,'assist':0,"year":datetime.now().strftime('%Y'),"month":datetime.now().strftime('%m')})
                            if usersHonorSerializer.is_valid():
                                usersHonorSerializer.save()
                # 设置贡献
                for user_id in gameMembersIdsHasRemarksOnly:
                    if instance.status == 0:
                        userHonor = UsersHonor.objects.filter(user_id=user_id,club=instance.club,year=datetime.now().strftime('%Y'),month=datetime.now().strftime('%m')).first()
                        contribute = gameMembersIdsHasRemarks.count(user_id)
                        if userHonor:
                            userHonor.contribute += contribute
                            userHonor.save()
                        else:
                            # 创建记录
                            usersHonorSerializer = UsersHonorSerializer(
                                data={'user': user_id, 'club': instance.club.id,'contribute': contribute,'goal':0,'assist':0,"year":datetime.now().strftime('%Y'),"month":datetime.now().strftime('%m')})
                            if usersHonorSerializer.is_valid():
                                usersHonorSerializer.save()

            instance.status = 1
            instance.club.save()
            instance.save()
            return Response({'msg': 'ok'}, status.HTTP_200_OK)
