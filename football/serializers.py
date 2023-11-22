from rest_framework import serializers
from .models import Users, Clubs, UsersClubs, UploadImages


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['id', 'nick_name', 'common_name', 'avatar']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in usefields:
                resData[field_name] = data[field_name]
        return resData


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
            role = UserClubsSerializer(instance.users_clubs_set.get(
                club_id=instance.id, user_id=i['id'])).data['role']
            i['role'] = role
            data['members'].append(i)
        return data


class UserClubsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersClubs
        fields = '__all__'


class UploadImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadImages
        fields = '__all__'
