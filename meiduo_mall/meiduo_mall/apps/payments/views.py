import os

from alipay import AliPay
from django.conf import settings
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from orders.models import OrderInfo

class PayMentView(APIView):
    """
        构造跳转链接
    """
    def get(self, request, order_id):
        #验证order_id是否存在
        try:
            order = OrderInfo.objects.get(order_id = order_id, pay_method=2,
                                          status=1)
        except:
            return Response("无效订单")

        #初始化支付
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/app_private_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/alipay_public_key.pem'),
            sign_type="RSA",  # RSA 或者 RSA2
            debug = settings.ALIPAY_DEBUG  # 默认False
        )

        #构建查询字符串

        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  #订单编号
            total_amount=str(order.total_amount), #订单总价
            subject='美多商城%s' % order_id,
            # return_url="https://example.com",
            # notify_url="https://example.com/notify"  # 可选, 不填则使用默认notify url
            return_url="http://www.meiduo.site:8080/pay_success.html",
        )

        alipay_url = settings.ALIPAY_URL + order_string

        return Response({
            'alipay_url': alipay_url
        })

