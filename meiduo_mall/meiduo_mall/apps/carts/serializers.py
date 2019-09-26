import re
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from drf_haystack.serializers import HaystackSerializer
from goods.models import SKU
from goods.search_indexes import SKUIndex
from oauth.models import OAuthQQUser


class CartSerializers(serializers.Serializer):
    sku_id = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=1)
    selected = serializers.BooleanField(default=True)

    def validate(self, attrs):
        #判断商品和库存
        try:
            sku = SKU.objects.get(id=attrs['sku_id'])
        except:
            raise serializers.ValidationError('商品不存在')

        if attrs['count'] > sku.stock:
            raise serializers.ValidationError('库存不足')

        return attrs

class CartDeleteSerializers(serializers.Serializer):
    sku_id = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        #判断商品和库存
        try:
            sku = SKU.objects.get(id=attrs['sku_id'])
        except:
            raise serializers.ValidationError('商品不存在')

        return attrs


class SKUSerializers(serializers.ModelSerializer):
    count = serializers.IntegerField(read_only=True)
    selected = serializers.BooleanField(read_only=True)

    class Meta:
        model = SKU
        fields = '__all__'

class CartSelectSerializers(serializers.Serializer):
    selected = serializers.BooleanField()
