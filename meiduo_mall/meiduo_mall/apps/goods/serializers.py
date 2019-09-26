import re
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from drf_haystack.serializers import HaystackSerializer
from goods.models import SKU
from goods.search_indexes import SKUIndex
from oauth.models import OAuthQQUser

from users.models import User

from rest_framework import serializers

from users.models import User


class SKUSerializers(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = '__all__'


class SKUSearchSerializer(HaystackSerializer):
    object = SKUSerializers(read_only=True)

    class Meta:
        index_classes = [SKUIndex]

        fields = ('text', 'object')


class SKUHistorySerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(min_value=1)

    # 判断商品是否存在

    def validate(self, attrs):
        try:
            SKU.objects.get(id=attrs['sku_id'])
        except:
            raise serializers.ValidationError('商品不存在')

        return attrs

    def create(self, validated_data):
        # 获取当前用户
        user = self.context['request'].user
        sku_id = validated_data['sku_id']
        # 建立缓存对象
        conn = get_redis_connection('history')
        # 判断sku_id是否存在列表
        pl = conn.pipeline()
        pl.lrem('history_%s' % user.id, 0, sku_id)
        # 写入缓存
        pl.lpush('history_%s' % user.id, sku_id)
        # 控制数量
        pl.ltrim('history_%s' % user.id, 0, 4)
        pl.execute()
        return validated_data
