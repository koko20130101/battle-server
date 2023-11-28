from rest_framework import serializers
from .models import Users, Clubs, UsersClubs, Apply, Playgrounds, Games, GameMembers, UploadImages


class ClubsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clubs
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['id', 'club_name', 'club_logo',
                     'sort', 'honor', 'brief']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in usefields:
                resData[field_name] = data[field_name]
        return resData


class UsersSerializer(serializers.ModelSerializer):
    clubs = serializers.ReadOnlyField(source='clubs.id')

    class Meta:
        model = Users
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['id', 'nick_name', 'common_name', 'avatar', 'clubs']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in usefields:
                resData[field_name] = data[field_name]
        return resData


class UsersDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['id', 'nick_name', 'common_name', 'avatar']
        data = super().to_representation(instance)
        resData = {}
        resData['clubs'] = []
        clubs = ClubsSerializer(instance.clubs, many=True).data
        print(clubs)
        for field_name in data:
            if field_name in usefields:
                resData[field_name] = data[field_name]
        return resData


class ClubsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clubs
        fields = '__all__'

    def to_representation(self, instance):
        # instance为一个Club的实例
        data = super().to_representation(instance)
        data['members'] = []
        # club实例的外键 instance.members ，检索出该队伍的人员
        members = UsersSerializer(instance.members, many=True).data
        for i in members:
            # 从中间表中检索出对应记录，为了获取扩展字段 role的值
            role = UsersClubsSerializer(instance.users_clubs_set.get(
                club_id=instance.id, user_id=i['id'])).data['role']
            i['role'] = role
            data['members'].append(i)
        return data


class UsersClubsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersClubs
        fields = '__all__'


class ApplySerializer(serializers.ModelSerializer):
    nick_name = serializers.ReadOnlyField(source='apply_user.nick_name')
    avatar = serializers.ReadOnlyField(source='apply_user.avatar')

    class Meta:
        model = Apply
        fields = '__all__'


class PlaygroundsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playgrounds
        fields = '__all__'


class GameMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameMembers
        fields = '__all__'


class GamesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Games
        fields = '__all__'

    def to_representation(self, instance):
        path = self.context['request'].path
        usefields = ['id', 'title', 'start_time',
                     'site', 'max_people', 'status', 'brief', 'battle', 'club']
        data = super().to_representation(instance)
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
