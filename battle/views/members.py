from rest_framework import viewsets, permissions, status, exceptions
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from battle.serializers import UsersClubsSerializer, UsersHonorSerializer
from battle.models import UsersClubs, UsersHonor,Clubs
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
                    goalNum += (honorItem['goal'] + honorItem['goal_out'])
                    assistNum += (honorItem['assist'] + honorItem['assist_out'])
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
    
    @action(methods=['GET'], detail=False, permission_classes=[])
    def ranking(self, request, *args, **kwargs):
        # 排行榜
        code = request.GET.get('code')
        year = request.GET.get('year')
        startMonth = request.GET.get('startMonth')
        endMonth = request.GET.get('endMonth')
        if not code:
            return Response({'msg': '球队Code不能为空'},status=status.HTTP_403_FORBIDDEN)
        if not year:
            return Response({'msg': '年份不能为空'},status=status.HTTP_403_FORBIDDEN)
        if not startMonth:
            return Response({'msg': '查询时间不能为空'},status=status.HTTP_403_FORBIDDEN)
        # 查询球队
        club = Clubs.objects.filter(code=code).first()
        queryset = self.filter_queryset(
            self.get_queryset()).filter(club=club.id)
        serializer = self.get_serializer(queryset, many=True)
        newMembers=[]
        result = {}
        for member in serializer.data:
            honorInfo = UsersHonor.objects.filter(user_id=member['user'],club_id=member['club'],year=year)
            if endMonth:
                honorInfo = honorInfo.filter(Q(month__gt= int(startMonth)-1) & Q(month__lt= int(endMonth)+1) )
            else:
                honorInfo = honorInfo.filter(month=startMonth)

            honorInfo = honorInfo.values()
            member.pop('user')
            member.pop('club')

            if honorInfo:
                honorNum = 0  # 出勤
                contributeNum = 0 # 贡献
                goalTotalNum = 0  # 总进球
                goalNum = 0  # 内战进球
                goalOutNum = 0  # 外战进球
                assistNum = 0  # 内战助攻
                assistOutNum = 0  # 外战助攻
                assistTotalNum = 0  # 助攻总和
                mvpNum = 0  # mvp
                for honorItem in honorInfo:
                    honorNum += honorItem['honor']
                    contributeNum += honorItem['contribute']
                    goalNum += honorItem['goal']
                    goalOutNum += honorItem['goal_out']
                    goalTotalNum += honorItem['goal']
                    goalTotalNum += honorItem['goal_out']
                    assistNum += honorItem['assist']
                    assistOutNum += honorItem['assist_out']
                    assistTotalNum += honorItem['assist']
                    assistTotalNum += honorItem['assist_out']
                    mvpNum += honorItem['mvp']
                member['honor'] = honorNum  # 出勤
                member['contribute'] = contributeNum  # 贡献
                member['goal_total'] = goalTotalNum  # 总进球
                member['goal'] = goalNum # 内战进球
                member['goal_out'] = goalOutNum  # 外战进球
                member['assist_total'] = assistNum # 总助攻
                member['assist_out'] = assistOutNum # 外战助攻
                member['assist'] = assistNum # 内战助攻
                member['mvp'] = mvpNum # mvp
                member['score'] = round(honorNum + contributeNum*0.5 + goalOutNum*2 + goalNum + assistNum*1.2 + assistOutNum*2 + mvpNum*3,1)
                newMembers.append(member)
            result['topContribute'] = sorted(newMembers,key=lambda x:x['contribute'],reverse=True)[0:1]  # 最佳贡献
            result['topGoal'] = sorted(newMembers,key=lambda x:x['goal_total'],reverse=True)[0:1]  # 最佳射手
            result['rankGoalOut'] = sorted(newMembers,key=lambda x:x['goal_out'],reverse=True)[0:10]  # 外战射手榜
            result['rankGoal'] = sorted(newMembers,key=lambda x:x['goal'],reverse=True)[0:10]  # 内战射手榜
            result['rankScore'] = sorted(newMembers,key=lambda x:x['score'],reverse=True)[0:10]  # 积分榜
            result['rankHonor'] = sorted(newMembers,key=lambda x:x['honor'],reverse=True)[0:10]  # 出勤榜
            result['rankAssistOut'] = sorted(newMembers,key=lambda x:x['assist_out'],reverse=True)[0:10]  # 外战助攻榜
            result['rankAssist'] = sorted(newMembers,key=lambda x:x['assist'],reverse=True)[0:10]  # 内战助攻榜
            result['rankContribute'] = sorted(newMembers,key=lambda x:x['contribute'],reverse=True)[0:10]  #贡献榜
            result['rankMvp'] = sorted(newMembers,key=lambda x:x['mvp'],reverse=True)[0:10]  #mvp榜

        return Response(result, status.HTTP_200_OK)
