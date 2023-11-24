from distutils.log import error
from django.db.models import Q
from django.core.cache import cache
from pymysql import NULL
from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from football.serializers import ApplySerializer, PlaygroundsSerializer, GamesSerializer, UploadImagesSerializer
from football.models import Clubs, Apply, Playgrounds, Games, UploadImages
from football.permissions import IsOwner
from config.settings import APP_ID, SECRET
from PIL import Image
from io import BytesIO


class ApplyViewSet(viewsets.ModelViewSet):
    queryset = Apply.objects.all()
    serializer_class = ApplySerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # 申请列表
        clubId = request.data.get('club')
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
        clubId = request.data.get('club')
        user = request.user

        if clubId:
            club = Clubs.objects.get(id=clubId)
            if club.need_apply:
                # 需要审核
                apply = self.get_queryset().filter(
                    club=club.id, apply_user=user.id).first()
                if apply:
                    return Response({'msg': '您已提交申请，请耐心等待管理员审核'}, status.HTTP_503_SERVICE_UNAVAILABLE)
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
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '请选择要加入的球队'})

    def perform_destroy(self, instance):
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '您无权操作'})

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def agree(self, request, *args, **kwargs):
        # 是否通过审核
        user = request.user
        applyId = request.data.get('applyId')
        clubId = request.data.get('club')
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
                    if active == '1':
                        club.members.add(apply.apply_user)
                        apply.delete()
                    if active == '2':
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


class GamesViewSet(viewsets.ModelViewSet):
    queryset = Games.objects.all()
    serializer_class = GamesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        clubs = user.clubs
        print(clubs)
        # queryset = self.filter_queryset(self.get_queryset()).filter(
        #     family=request.user.belong_family)
        # serializer = self.get_serializer(queryset, many=True)
        # return Response(serializer.data)


class ImageUploadViewSet(viewsets.ModelViewSet):
    '''上传图片视图集'''
    queryset = UploadImages.objects.all()
    serializer_class = UploadImagesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
