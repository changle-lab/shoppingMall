import re
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJS

from oauth.models import OAuthQQUser

from users.models import User

from rest_framework import serializers

from users.models import User


class OauthSerializer(serializers.ModelSerializer):
# sms_code = serializers.CharField(max_length=6, min_length=6,
# 显示指明字段
    #                                  write_only=True)
    # access_token = serializers.CharField(write_only=True)
    # mobile = serializers.CharField(max_length=11, min_length=11)
    # class Meta:
    #     model = User
    #     fields = ('mobile', 'password', 'access_token')
    #     extra_kwargs = {
    #         'password': {
    #             'write_only': True,
    #             'max_length': 20,
    #             'min_length': 8
    #         }
    #     }
    #
    #

    pass

class OauthSerializer(serializers.ModelSerializer):
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    access_token = serializers.CharField(write_only=True)

    mobile = serializers.CharField(max_length=11, min_length=11)

    token = serializers.CharField(read_only=True)

    username = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('mobile', 'password', 'sms_code', 'access_token', 'token', 'username')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8
            }

        }

    # 验证手机号格式
    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机格式不匹配')

        return value

    def validate(self, attrs):
        # 验证码判断
        # 1、获取缓存中真实的短信验证码
        conn = get_redis_connection('sms_code')
        real_sms_code = conn.get('sms_code_%s' % attrs['mobile'])
        # 2、判断短信验证码是否失效
        if real_sms_code is None:
            raise serializers.ValidationError('短信验证码已失效')
        # 3、比对用户输入的短信验证码
        if attrs['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('输入的短信验证码错误')

        # accesstoken判断
        tjs = TJS(settings.SECRET_KEY, 300)

        # 解密   accesstoken
        try:
            data = tjs.loads(attrs['access_token'])  # {openid:asdasdasd}
        except:
            raise serializers.ValidationError('错误的access_token')

        # 获取openid
        openid = data.get('openid')
        if openid is None:
            raise serializers.ValidationError('无效的access_token')

        attrs['openid'] = openid

        # 查询用户
        try:
            user = User.objects.get(mobile=attrs['mobile'])
        except:
            # 用户不存在
            return attrs  # 没有 user
        else:
            # 用户存在
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError('密码错误')
            attrs['user'] = user
            return attrs  # 有user

    def create(self, validated_data):

        # 判断是否有user
        user = validated_data.get('user')
        if user is None:
            user = User.objects.create_user(username=validated_data['mobile'], password=validated_data['password'],
                                            mobile=validated_data['mobile'])

        # 绑定openid
        OAuthQQUser.objects.create(user=user, openid=validated_data['openid'])

        # 生成jwt token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        # 给user对象添加token属性
        user.token = token
        return user
