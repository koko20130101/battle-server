from rest_framework import serializers
from .models import Users, Clubs, UsersClubs, Apply, Playgrounds, Games, GameMembers, UploadImages
import time


class ClubsSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.nick_name')

    class Meta:
        model = Clubs
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['id', 'club_name', 'short_name', 'club_logo',
                     'sort', 'honor', 'brief', 'creator', 'need_apply', 'area', 'area_code']
        data = super().to_representation(instance)
        resData = {}
        members = UsersSerializer(instance.members, many=True).data
        resData['memberTotal'] = len(members)

        for field_name in data:
            if field_name in usefields:
                resData[field_name] = data[field_name]
        return resData


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['id', 'nick_name', 'avatar']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in usefields:
                resData[field_name] = data[field_name]
        return resData


class UsersClubsSerializer(serializers.ModelSerializer):
    nickName = serializers.ReadOnlyField(source='user.nick_name')
    avatar = serializers.ReadOnlyField(source='user.avatar')

    class Meta:
        model = UsersClubs
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['id', 'role', 'nickName', 'avatar']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in usefields:
                resData[field_name] = data[field_name]
        return resData


class ApplySerializer(serializers.ModelSerializer):
    nickName = serializers.ReadOnlyField(source='apply_user.nick_name')
    avatar = serializers.ReadOnlyField(source='apply_user.avatar')

    class Meta:
        model = Apply
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['id', 'nickName', 'avatar', 'remarks']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in usefields:
                resData[field_name] = data[field_name]
        return resData


class PlaygroundsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playgrounds
        fields = '__all__'


class GameMembersSerializer(serializers.ModelSerializer):
    nickName = serializers.ReadOnlyField(source='user.nick_name')
    avatar = serializers.ReadOnlyField(source='user.avatar')
    class Meta:
        model = GameMembers
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['id','user', 'nickName', 'avatar', 'remarks','cost']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in usefields:
                resData[field_name] = data[field_name]
        return resData


class GamesSerializer(serializers.ModelSerializer):
    clubName = serializers.ReadOnlyField(source='club.club_name')
    clubLogo = serializers.ReadOnlyField(source='club.club_logo')
    class Meta:
        model = Games
        fields = '__all__'

    def to_representation(self, instance):
        path = self.context['request'].path
        usefields = ['id', 'title', 'game_date', 'start_time', 'end_time',
                     'site', 'max_people', 'status', 'brief', 'battle', 'club','clubName','tag']
        data = super().to_representation(instance)
        if data['start_time'] and data['end_time']:
            t1 = time.strptime(
                data['start_time'], '%Y-%m-%dT%H:%M:%S+08:00')
            t2 = time.strptime(
                data['end_time'], '%Y-%m-%dT%H:%M:%S+08:00')
            data['game_date'] = time.strftime('%Y-%m-%d', t1)
            data['start_time'] = time.strftime('%H:%M', t1)
            data['end_time'] = time.strftime('%H:%M', t2)
        resData = {}
        if path == '/games':
            # 列表输出给定字段
            for field_name in data:
                if field_name in usefields:
                    resData[field_name] = data[field_name]
        else:
            resData = data
        return resData


class UploadImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadImages
        fields = '__all__'
