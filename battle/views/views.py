from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from battle.serializers import ApplySerializer, PlaygroundsSerializer, UsersClubsSerializer, UploadImagesSerializer
from battle.models import Clubs, UsersClubs, Apply, Playgrounds,  UploadImages


class MembersViewSet(viewsets.ModelViewSet):
    '''球队成员视图集'''
    queryset = UsersClubs.objects.all()
    serializer_class = UsersClubsSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 指定可以过滤字段
    # filterset_fields = ['playground_name']
    # 对特定字段进行排序,指定排序的字段
    ordering_fields = ['id']

    def list(self, request, *args, **kwargs):
        user = request.user
        clubId = request.GET.get('clubId')
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
        return Response(serializer.data, status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})

    def update(self, request, *args, **kwargs):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})

    def retrieve(self, request, *args, **kwargs):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权查看'})


class ApplyViewSet(viewsets.ModelViewSet):
    queryset = Apply.objects.all()
    serializer_class = ApplySerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # 申请列表
        clubId = request.GET.get('clubId')
        user = request.user
        club = Clubs.objects.filter(creator=user.id, id=clubId).first()
        if club:
            queryset = self.filter_queryset(
                self.get_queryset()).filter(club=clubId)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
            else:
                serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({'msg': '找不到记录'}, status.HTTP_503_SERVICE_UNAVAILABLE)

    def create(self, request, *args, **kwargs):
        # 申请
        clubId = request.data.get('clubId')
        user = request.user

        if clubId:
            club = Clubs.objects.get(id=clubId)
            if club.need_apply:
                
                # 需要审核
                apply = self.get_queryset().filter(
                    club=club.id, apply_user=user.id).first()
                if apply:
                    return Response({'msg': '您已提交过申请，请务重复申请'}, status.HTTP_503_SERVICE_UNAVAILABLE)
                else:
                    applyData = {
                        'club': club.id,
                        'apply_user': user.id,
                        'remarks': request.data.get('remarks')
                    }
                    serializer = self.get_serializer(data=applyData)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response({'msg': '申请成功，请耐心等待管理员审核'}, status.HTTP_200_OK)
            else:
                # 不需要审核，直接加入
                club.members.add(user, through_defaults={'role': 3})
                return Response({'msg': '加入成功'}, status.HTTP_200_OK)

        else:
            return Response({'msg': '请选择要加入的球队'}, status.HTTP_403_FORBIDDEN)

    def perform_destroy(self, instance):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def agree(self, request, *args, **kwargs):
        # 同意
        user = request.user
        applyId = request.data.get('applyId')
        clubId = request.data.get('clubId')
        # active 为1：通过，2：拒绝
        active = request.data.get('active')
        club = Clubs.objects.get(id=clubId)
        if not applyId:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': 'ID不能为空'})

        if club and club.creator.id == user.id:
            for id in applyId.split(','):
                apply = self.get_queryset().filter(id=id).first()
                if apply:
                    if active == 1:
                        club.members.add(apply.apply_user)
                        apply.delete()
                    if active == 2:
                        apply.delete()
            return Response({'msg': 'ok'}, status.HTTP_200_OK)
        else:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})


class PlaygroundsViewSet(viewsets.ModelViewSet):
    '''球场视图集'''
    queryset = Playgrounds.objects.all()
    serializer_class = PlaygroundsSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 指定可以过滤字段
    filterset_fields = ['playground_name']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


class ImageUploadViewSet(viewsets.ModelViewSet):
    '''上传图片视图集'''
    queryset = UploadImages.objects.all()
    serializer_class = UploadImagesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
