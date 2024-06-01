from rest_framework import viewsets, permissions, status, exceptions
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from battle.serializers import UsersClubsSerializer, UsersHonorSerializer
from battle.models import UsersClubs, UsersHonor
from battle.permissions import ReadOnly


class MembersViewSet(viewsets.ModelViewSet):
    '''球队成员视图集'''
    queryset = UsersClubs.objects.all()
    serializer_class = UsersClubsSerializer
    permission_classes = [permissions.IsAuthenticated, ReadOnly]
    # 指定可以过滤字段
    # filterset_fields = ['playground_name']
    # 对特定字段进行排序,指定排序的字段
    ordering_fields = ['id']

    def list(self, request, *args, **kwargs):
        user = request.user
        clubId = request.GET.get('clubId')
        year = request.GET.get('year')
        month = request.GET.get('month')
        # 是否是球队成员
        members = self.filter_queryset(
            self.get_queryset()).filter(user=user, club=clubId)

        if members.first():
            queryset = self.filter_queryset(
                self.get_queryset()).filter(club=clubId)
            page = self.paginate_queryset(queryset)
        else:
            page = self.paginate_queryset(members)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)
        result=[]
        for member in serializer.data:
            honorInfo = UsersHonor.objects.filter(user_id=member['user'],club_id=member['club'])
            if year:
                honorInfo = honorInfo.filter(year=year)
            if month:
                honorInfo = honorInfo.filter(month=month)
            honorInfo = honorInfo.values()
            
            member.pop('user')
            member.pop('club')
            if honorInfo:
                honorNum = 0
                contributeNum = 0
                goalNum = 0
                assistNum = 0
                for honorItem in honorInfo:
                    honorNum += honorItem['honor']
                    contributeNum += honorItem['contribute']
                    goalNum += honorItem['goal']
                    assistNum += honorItem['assist']
                member['honor'] = honorNum
                member['contribute'] = contributeNum
                member['goal'] = goalNum
                member['assist'] = assistNum
            else:
                member['honor'] = 0
                member['contribute'] = 0
                member['goal'] = 0
                member['assist'] = 0
            result.append(member)
        return Response(result, status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})

    def update(self, request, *args, **kwargs):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})

    def retrieve(self, request, *args, **kwargs):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权查看'})

    def destroy(self, request, *args, **kwargs):
        # 不能删除
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})
