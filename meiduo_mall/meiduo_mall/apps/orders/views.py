from decimal import Decimal

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from orders.serializers import OrderSerializers, SaveOrderSerializer



class OrdersView(APIView):

    def get(self, request):

        # 1:获取当前用户
        user = request.user
        # 2:建立redis链接
        conn = get_redis_connection('cart')
        # 3:获取选中状态的cku_id和count

        sku_id_count = conn.hgetall('cart_%s' % user.id)  # 获取购物车中的商品对象,有count属性
        sku_ids = conn.smembers('cart_selected_%s' % user.id)  # 获取选中的商品id
        # 合并数据
        cart = {}
        for sku_id in sku_ids:
            cart[int(sku_id)] = int(sku_id_count[sku_id])


        # 查询选中商品状态的对象,这个是去数据库中查询了
        skus = SKU.objects.filter(id__in=cart.keys())
        # 5:序列化返回
        for sku in skus:
            sku.count = cart[sku.id]

        freight = Decimal(10)
        ser = OrderSerializers({'freight': freight, 'skus': skus})

        return Response(ser.data)


class SaveOrderView(CreateAPIView):
    """
        保存订单
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SaveOrderSerializer
