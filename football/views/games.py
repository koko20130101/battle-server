from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from football.serializers import GamesSerializer
from football.models import Clubs, UsersClubs, Games


class GamesViewSet(viewsets.ModelViewSet):
    queryset = Games.objects.all()
    serializer_class = GamesSerializer
    permission_classes = [permissions.IsAuthenticated]

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

    def retrieve(self, request, *args, **kwargs):
        # 详情
        user = request.user
        instance = self.get_object()
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club).first()
        if user_blub:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def perform_create(self, serializer):
        # 创建
        user = self.request.user
        clubId = self.request.data.get('club')
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

    def perform_destroy(self, instance):
        # 删除
        user = self.request.user
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=instance.club).first()
        if user_blub and user_blub.role in [1, 2]:
            instance.delete()
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})

    def perform_update(self, serializer):
        # 编辑
        user = self.request.user
        clubId = self.request.data.get('club')
        user_blub = UsersClubs.objects.filter(
            user_id=user.id, club_id=clubId).first()

        if user_blub and user_blub.role in [1, 2]:
            serializer.save()
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})
