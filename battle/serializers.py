from rest_framework import serializers
from .models import Users, Clubs, UsersClubs, Apply, BattleApply, Playgrounds, ClubsPlaygrounds, Games, GameMembers, UploadImages, ClubAccount, Account, AccountRecord, Advert, Message
import time
from datetime import datetime, timedelta


class ClubsSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.nick_name')

    class Meta:
        model = Clubs
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['id', 'club_name', 'short_name', 'club_logo', 'club_type',
                     'sort', 'honor', 'brief', 'creator', 'need_apply', 'area', 'area_code', 'main_playground']
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
        usefields = ['id', 'nick_name', 'avatar', 'honor','created']
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


class ClubsPlaygroundsSerializer(serializers.ModelSerializer):
    playgroundName = serializers.ReadOnlyField(
        source='playground.playground_name')
    playgroundId = serializers.ReadOnlyField(source='playground.id')

    class Meta:
        model = ClubsPlaygrounds
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['id', 'playgroundName', 'playgroundId']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in usefields:
                resData[field_name] = data[field_name]
        return resData


class GameMembersSerializer(serializers.ModelSerializer):
    nickName = serializers.ReadOnlyField(source='user.nick_name')
    avatar = serializers.ReadOnlyField(source='user.avatar')

    class Meta:
        model = GameMembers
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['id', 'user', 'nickName',
                     'avatar', 'remarks', 'cost', 'free']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in usefields:
                resData[field_name] = data[field_name]
        return resData


class GamesSerializer(serializers.ModelSerializer):
    clubName = serializers.ReadOnlyField(source='club.club_name')
    clubLogo = serializers.ReadOnlyField(source='club.club_logo')
    rivalName = serializers.ReadOnlyField(source='battle.club.club_name')
    rivalLogo = serializers.ReadOnlyField(source='battle.club.club_logo')
    site = serializers.ReadOnlyField(
        source='playground.playground_name')

    class Meta:
        model = Games
        fields = '__all__'

    def to_representation(self, instance):
        path = self.context['request'].path
        usefields = ['id', 'title', 'game_date', 'start_time', 'end_time', 'open_battle', 'competition',
                     'site', 'min_people', 'max_people', 'status', 'brief', 'rivalName', 'rivalLogo', 'club', 'clubName', 'clubLogo', 'tag']
        data = super().to_representation(instance)
        if data['start_time'] and data['end_time']:

            # data['end_time'].timestamp() < (datetime.now() - timedelta(days=1)).timestamp()
            t1 = time.strptime(
                data['start_time'], '%Y-%m-%dT%H:%M:%S+08:00')
            t2 = time.strptime(
                data['end_time'], '%Y-%m-%dT%H:%M:%S+08:00')
            d2 = datetime.strptime(data['end_time'], '%Y-%m-%dT%H:%M:%S+08:00')
            if (d2+timedelta(hours=12)).timestamp() > datetime.now().timestamp() > d2.timestamp():
                # 可结算：结束时间之后12小时内可结算
                data['canSettlement'] = True
            data['game_date'] = time.strftime('%Y-%m-%d', t1)
            data['start_time'] = time.strftime('%H:%M', t1)
            data['end_time'] = time.strftime('%H:%M', t2)
        resData = {}
        if path == '/games' or path == '/games/openGames':
            # 列表输出给定字段
            for field_name in data:
                if field_name in usefields:
                    resData[field_name] = data[field_name]
        else:
            members = GameMembers.objects.all().filter(game=instance.id)
            # 总报名人数
            data['joinTotal'] = len(members)
            resData = data
        return resData


class BattleApplySerializer(serializers.ModelSerializer):
    clubName = serializers.ReadOnlyField(source='rival.club.club_name')

    class Meta:
        model = BattleApply
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['id', 'clubName', 'remarks']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in usefields:
                resData[field_name] = data[field_name]
        return resData


class ClubAccountSerializer(serializers.ModelSerializer):
    playgroundName = serializers.ReadOnlyField(
        source='playground.playground_name')

    class Meta:
        model = ClubAccount
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    playgroundName = serializers.ReadOnlyField(
        source='playground.playground_name')
    clubName = serializers.ReadOnlyField(
        source='club.club_name')

    class Meta:
        model = Account
        fields = '__all__'


class AccountRecordSerializer(serializers.ModelSerializer):
    playgroundName = serializers.ReadOnlyField(
        source='playground.playground_name')
    userName = serializers.ReadOnlyField(
        source='user.nick_name')
    clubName = serializers.ReadOnlyField(
        source='club.club_name')

    class Meta:
        model = AccountRecord
        fields = '__all__'


class UploadImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadImages
        fields = '__all__'


class AdvertSerializer(serializers.ModelSerializer):

    class Meta:
        model = Advert
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
