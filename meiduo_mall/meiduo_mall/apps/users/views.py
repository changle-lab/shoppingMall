from django.conf import settings
from django.shortcuts import render
from random import randint

# Create your views here.
from django_redis import get_redis_connection
# from rest_framework import serializers
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from celery_tasks.sms_code.tasks import send_sms_code
from rest_framework.views import APIView
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from libs.yuntongxun.sms import CCP
from users.models import User

# 发送短信
# from users.serializers import UserSerializers
from users.serializers import UserSerializer, UserShowSerializers, UserEmailSerializers


class SMS_Code_View(APIView):

    def get(self, request, mobile):
        # 获取参数即手机号
        # 验证手机号
        # 判断请求的间隔
        conn = get_redis_connection('sms_code')
        flag = conn.get("sms_code_flag_%s" % mobile)
        # if flag:
        #     return Response({'error': '请求过于频繁'}, status=403)

        # 生成短信验证码
        sms_code = "%06d" % randint(0, 999999)
        print(sms_code)
        # 储存到redis
        conn = get_redis_connection('sms_code')
        pl = conn.pipeline()
        pl.setex("sms_code_%s" % mobile, 300, sms_code)
        # 写入一个标志数据
        pl.setex("sms_code_flag_%s" % mobile, 60, 2)
        pl.execute()
        # 发送短信
        # ccp = CCP()
        # ccp.send_template_sms(mobile, [sms_code, '5'], 1)
        send_sms_code.delay(mobile, sms_code)

        # 返回结果
        return Response("OK")


# 验证用户名是否重复
class UserNameView(APIView):
    """
    判断用户名是否重复
    """

    def get(self, request, username):
        count = User.objects.filter(username=username).count()

        return Response({'count': count})


# 验证手机号是否重复
class MobileView(APIView):
    """
    判断手机号是否重复
    """

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()

        return Response({'count': count})


# 注册
class UserView(CreateAPIView):
    """
    注册
    """
    # serializer_class = UserSerializers
    serializer_class = UserSerializer

#个人中心——展示用户信息
class UserShowView(RetrieveAPIView):

    serializer_class = UserShowSerializers


    queryset = User.objects.all()

    def get_object(self):

        return self.request.user

class UserEmailView(UpdateAPIView):

    serializer_class = UserEmailSerializers

    def get_object(self):

        return self.request.user


class UserEmailVifyView(APIView):
    """
        邮箱验证
    """

    def get(self, request):
        # 获取前段数据
        token = request.query_params.get('token')
        # 解密token
        tjs = TJS(settings.SECRET_KEY, 300)
        try:
            data = tjs.loads(token)
        except:
            return Response({'errors': '错误的token'}, status=400)
        # 获取用户数据
        username = data.get('username')
        # username
        # 查询用户对象
        user = User.objects.get(username = username)
        # 更新用户的邮箱验证状态
        user.email_active=True
        user.save()
        # 返回验证状态
        return Response({'email_active': user.email_active})



