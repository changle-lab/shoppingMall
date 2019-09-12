from QQLoginTool.QQtool import OAuthQQ
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from urllib.parse import urlencode
from django.shortcuts import render


# Create your views here.


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



