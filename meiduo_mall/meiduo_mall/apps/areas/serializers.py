import re
from rest_framework import serializers
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from users.models import Address

from areas.models import Area
from oauth.models import OAuthQQUser
from users.models import User


class AreasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id', 'name')


class AddressSerializer(serializers.ModelSerializer):
    city_id = serializers.IntegerField(write_only=True)
    district_id = serializers.IntegerField(write_only=True)
    province_id = serializers.IntegerField(write_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Address

        fields = ('title', 'receiver', 'province_id',
                  'city_id', 'district_id', 'place', 'mobile', 'tel',
                  'email', 'city', 'district', 'province', 'id')

    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        user = self.context['request'].user

        validated_data['user'] = user

        address = Address.objects.create(**validated_data)

        return address



