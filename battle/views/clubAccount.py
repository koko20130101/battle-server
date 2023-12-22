from rest_framework import viewsets, permissions, status, exceptions
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from battle.serializers import ClubAccountSerializer, ClubAccountRecordSerializer
from battle.models import ClubAccount, ClubAccountRecord, Clubs


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
            memberIds = list(i.id for i in club.members.all())
            instance = self.filter_queryset(
                self.get_queryset()).filter(club=club, playground=playground).first()
            clubAccountRecord = ClubAccountRecordSerializer(
                data={'amount': sum, 'amount_type': 1, 'club': club.id, 'playground': playground})
            if instance:
                instance.balance += float(sum)
                instance.save()
                clubAccountRecord.is_valid(raise_exception=True)
                print(clubAccountRecord.data)
                clubAccountRecord.save()
                return Response({'msg': '成功'}, status.HTTP_200_OK)
            else:
                # 新账户
                accountData = {
                    'club': club.id,
                    'playground': playground,
                    'balance': float(sum)
                }
                serializer = self.get_serializer(data=accountData)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                clubAccountRecord.save()
                return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response({'msg': '非法操作'}, status.HTTP_403_FORBIDDEN)


class ClubAccountRecordViewSet(viewsets.ModelViewSet):
    '''球队账户明细视图集'''
    queryset = ClubAccountRecord.objects.all()
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
