from rest_framework import serializers
from .models import Users


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
