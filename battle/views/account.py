from rest_framework import viewsets, permissions, status, exceptions
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from battle.serializers import ClubAccountSerializer, AccountRecordSerializer, AccountSerializer, AccountRecordSerializer
from battle.models import ClubAccount, AccountRecord, Clubs, Account, UsersClubs


class ClubAccountViewSet(viewsets.ModelViewSet):
    '''球队账户视图集'''
    queryset = ClubAccount.objects.all()
    serializer_class = ClubAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        clubId = request.GET.get('clubId')
        if not clubId:
            return Response({'msg': '球队ID不能为空'}, status.HTTP_503_SERVICE_UNAVAILABLE)
        instance = Clubs.objects.all().filter(id=clubId).first()
        if instance.creator == user:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response({'msg': '非法操作'}, status.HTTP_403_FORBIDDEN)

    def perform_update(self, request, *args, **kwargs):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def perform_destroy(self, instance):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def recharge(self, request, *args, **kwargs):
        # 充值
        user = request.user
        clubId = request.data.get('clubId')
        sum = request.data.get('sum')
        playground = request.data.get('playground')
        memberId = request.data.get('memberId')
        if not clubId:
            return Response({'msg': '球队ID不能为空'}, status.HTTP_503_SERVICE_UNAVAILABLE)
        if not sum:
            return Response({'msg': '金额不能为空'}, status.HTTP_503_SERVICE_UNAVAILABLE)
        if not playground:
            return Response({'msg': '球场不能为空'}, status.HTTP_503_SERVICE_UNAVAILABLE)

        club = Clubs.objects.all().filter(id=clubId).first()
        if club.creator == user:
            instance = self.filter_queryset(
                self.get_queryset()).filter(club=club, playground=playground).first()
            memberUser = UsersClubs.objects.all().filter(
                id=memberId if memberId != '' else None).first()
            accountRecord = AccountRecordSerializer(
                data={'amount': sum, 'amount_type': 1, 'club': club.id, 'user': memberUser.user.id if memberUser else None, 'playground': playground})
            if instance:
                instance.balance += float(sum)
                instance.save()
                if accountRecord.is_valid():
                    accountRecord.save()
            else:
                # 新账户
                accountData = {
                    'club': club.id,
                    'playground': playground,
                    'balance': float(sum)
                }
                serializer = self.get_serializer(data=accountData)
                if serializer.is_valid() and accountRecord.is_valid():
                    serializer.save()
                    accountRecord.save()
            if memberId and memberUser:
                account = Account.objects.all().filter(
                    user=memberUser.user.id, club=club.id, playground=playground).first()
                if account:
                    account.balance += float(sum)
                    account.save()
                else:
                    accountSerializer = AccountSerializer(
                        data={'balance': sum, 'account_type': 1, 'club': club.id, 'user': memberUser.user.id, 'playground': playground})
                    if accountSerializer.is_valid():
                        accountSerializer.save()
            return Response({'msg': '成功'}, status.HTTP_200_OK)
        else:
            return Response({'msg': '非法操作'}, status.HTTP_403_FORBIDDEN)


class AccountViewSet(viewsets.ModelViewSet):
    '''账户视图集'''
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = self.filter_queryset(
            self.get_queryset()).filter(user=user.id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def perform_update(self, request, *args, **kwargs):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def perform_destroy(self, instance):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})


class AccountRecordViewSet(viewsets.ModelViewSet):
    '''账户明细视图集'''
    queryset = AccountRecord.objects.all()
    serializer_class = AccountRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 对特定字段进行排序,指定排序的字段
    ordering_fields = ['id']

    def list(self, request, *args, **kwargs):
        user = request.user
        clubId = request.GET.get('clubId')

        if clubId:
            # 球队的账户明细
            instance = Clubs.objects.all().filter(id=clubId).first()
            if instance.creator == user:
                queryset = self.filter_queryset(
                    self.get_queryset()).filter(Q(club=clubId, amount_type=1) | Q(club=clubId, user=None))
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                else:
                    serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data, status.HTTP_200_OK)
        else:
            # 用户的账户明细
            queryset = self.filter_queryset(
                self.get_queryset()).filter(user=user.id)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
            else:
                serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def perform_update(self, request, *args, **kwargs):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def perform_destroy(self, instance):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})
