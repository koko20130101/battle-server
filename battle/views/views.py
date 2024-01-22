from rest_framework import viewsets, permissions, status, exceptions
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from battle.serializers import ApplySerializer, UploadImagesSerializer, AdvertSerializer, MessageSerializer
from battle.models import Clubs, Apply,  UploadImages, Advert, Message
from battle.permissions import ReadOnly

class ApplyViewSet(viewsets.ModelViewSet):
    queryset = Apply.objects.all()
    serializer_class = ApplySerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # 申请列表
        clubId = request.GET.get('clubId')
        user = request.user
        club = Clubs.objects.filter(creator_id=user.id, id=clubId).first()
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
            if club.members.filter(id=user.id).first():
                return Response({'msg': '您已经在球队中！'}, status.HTTP_503_SERVICE_UNAVAILABLE)
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

    def update(self, request, *args, **kwargs):
        # 不能put更新
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def retrieve(self, request, *args, **kwargs):
        # 不能看详情
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def perform_destroy(self, instance):
        # 不能删除
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

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


class ImageUploadViewSet(viewsets.ModelViewSet):
    '''上传图片视图集'''
    queryset = UploadImages.objects.all()
    serializer_class = UploadImagesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


class AdvertViewSet(viewsets.ModelViewSet):
    '''广告位视图集'''
    queryset = Advert.objects.all()
    serializer_class = AdvertSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # 指定可以过滤字段
    filterset_fields = ['ad_type']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset()).filter(status=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    '''消息中心视图集'''
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 指定可以过滤字段
    filterset_fields = ['m_type']
    ordering_fields = ['created']

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = self.filter_queryset(
            self.get_queryset()).filter(Q(owner=user) | Q(m_type=3))
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = serializer.data
            for i in page:
                if i.readed == False:
                    i.readed = True
                    i.save()
            return self.get_paginated_response(result)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(owner=user)

    def perform_update(self, serializer):
        # 不能修改公告类型
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def perform_destroy(self, instance):
        # 不能删除
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def unread(self, request, *args, **kwargs):
        # 未读消息
        user = request.user
        queryset = self.filter_queryset(
            self.get_queryset()).filter(Q(owner=user, readed=False) | Q(m_type=3, readed=False))
        serializer = self.get_serializer(queryset, many=True)
        return Response({'total': len(serializer.data)}, status.HTTP_200_OK)
