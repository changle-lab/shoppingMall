from QQLoginTool.QQtool import OAuthQQ
from rest_framework import request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from django.shortcuts import render

# Create your views here.
from rest_framework_jwt.settings import api_settings

from carts.utils import merge_cart_cookie_to_redis
from oauth.models import OAuthQQUser
from oauth.serializers import OauthSerializer
from users.models import User


class QQLoginUrlView(APIView):

    def get(self, request):
        next = request.query_params.get('next')
        if next is None:
            next = '/'

        # 生成QQ对象，调用QQ封装好的方法
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                     client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI,
                     state=next)

        # 调用 生成扫码页面对应url 的方法
        login_url = qq.get_qq_url()

        # 返回url

        return Response({'login_url': login_url})


class QQAuthUserView(CreateAPIView):
    # 制定序列化器验证用户数据
    serializer_class = OauthSerializer

    """
     获取openid，绑定openid
    """

    def get(self, request):

        # 获取code值
        code = request.query_params.get("code")
        if not code:
            return Response({'message': '缺少code'}, status=400)

        # 获取access_token值
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                     client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI,
                     state='/')

        access_token = qq.get_access_token(code)

        openid = qq.get_open_id(access_token)
        try:
            QQuser = OAuthQQUser.objects.get(openid=openid)
        except:
            tjs = TJS(settings.SECRET_KEY, 300)
            data = tjs.dumps({'openid': openid}).decode()

            return Response({'access_token': data})


        else:
            user = QQuser.user

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            # data = {
            #     'user_id': user.id,
            #     'username': user.name,
            #     'token': token
            # }
            response = Response({
                'user_id': user.id,
                'username': user.username,
                'token': token})
            response = merge_cart_cookie_to_redis(request, user, response)

            return response

    # def post(self, request):
    #     datas = request.data
    #     print(datas)
    #     password = datas['password']
    #     sms_code = datas['sms_code']
    #     mobile = datas['mobile']
    #     access_token = datas['access_token']
    #     print(password)
    #     print(mobile)
    #     print(sms_code)
    #     print(access_token)
    #     user = User.objects.get(mobile=mobile)
    #     user_id = user.id
    #     print('user_id:%s' % user_id)
    #     username = user.username
    #     print('username:%s' % username)
    #     tjs = TJS(settings.SECRET_KEY, 300)
    #     data = tjs.loads(access_token)
    #     openid = data.get('openid')
    #     qquser = OAuthQQUser(user=user, openid=access_token)
    #     # qquser.save()
    #
    #
    #     jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    #     jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    #     payload = jwt_payload_handler(user)
    #     token = jwt_encode_handler(payload)
    #
    #     # response = Response({
    #     #     'token': token,
    #     #     'user_id': user.id,
    #     #     'usesrname': user.username,
    #     #
    #     # })
    #     attrs = {}
    #     attrs['openid'] = openid
    #     attrs['user'] = user
    #     return attrs


