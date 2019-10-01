from datetime import datetime
import re
from decimal import Decimal

from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from django.db import transaction

from goods.models import SKU
from oauth.models import OAuthQQUser
from orders.models import OrderInfo, OrderGoods

from users.models import User

from rest_framework import serializers

from users.models import User


class OrderSKUSerializers(serializers.ModelSerializer):
    count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SKU
        fields = '__all__'

class OrderSerializers(serializers.Serializer):
    freight = serializers.DecimalField(max_digits=10, decimal_places=2)

    skus = OrderSKUSerializers(many=True)


# @transaction.atomic
class SaveOrderSerializer(serializers.ModelSerializer):
    """
    下单数据序列化器
    """
    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        """保存订单"""
        #获取用户数据和地址,支付方式
        user = self.context['request'].user
        address = validated_data['address']
        # address = "地址"
        pay_method = validated_data['pay_method']
        #生成订单编号
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + '%09d' % user.id
        #设置事务
        with transaction.atomic():
            # 设置保存点
            save_point = transaction.savepoint()
            try:
                # 3、初始化生成订单基本信息表
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    address=address,
                    user=user,
                    total_count=0,
                    total_amount=Decimal(0),
                    freight=Decimal(10),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'CASH'] else OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                )
                # 4、查询选中状态的sku——id对应的sku商品
                # 建立redis连接
                conn = get_redis_connection('cart')
                # 获取选中状态的sku_id和count
                sku_id_count = conn.hgetall('cart_%s' % user.id)
                sku_ids = conn.smembers('cart_selected_%s' % user.id)
                # 合并数据
                cart = {}  # {15:1}
                for sku_id in sku_ids:
                    cart[int(sku_id)] = int(sku_id_count[sku_id])
                # 查询寻中状态的商品对象
                # skus = SKU.objects.filter(id__in=cart.keys())

                # 5、遍历所有sku商品
                for sku_id in sku_ids:
                    sku = SKU.objects.get(id=sku_id)
                    # 6、获取当前sku商品原始库存和销量
                    old_stock = sku.stock
                    old_sales = sku.sales
                    sku_count = cart[sku.id]
                    # 7、判断购买数量是否大于库存
                    if sku_count > old_stock:
                        raise serializers.ValidationError('困存不足')
                    # 8、不大于库存，则修改sku商品的库存量和销量
                    # sku.stock = old_stock - sku_count
                    # sku.sales = old_sales + sku_count
                    # sku.save
                    new_stock = old_stock-sku_count
                    new_salse = old_sales+sku_count
                    ret = SKU.objects.filter(id=sku_id,stock=old_stock).update(
                        stock=new_stock,sales=new_salse
                    )

                    if ret==0:
                        continue


                    # 9、修改spu表中的总销量
                    sku.goods.sales += sku_count
                    sku.goods.save()
                    # 10、修改订单基本信息表中的总量和总价
                    order.total_amount += (sku.price * sku_count)
                    order.total_count += sku_count
                    # 11、保存订单商品表
                    OrderGoods.objects.create(
                        order=order,
                        sku=sku,
                        count=sku_count,
                        price=sku.price,
                    )
                    break

                # 累加运费
                order.total_amount += order.freight
                order.save()


            except:
                transaction.savepoint_rollback(save_point)

            else:
                transaction.savepoint_commit(save_point)

                #删除选中状态的商品
                conn.hdel('cart_%s' % user.id, *sku_ids)
                conn.srem('cart_selected_%s' % user.id, *sku_ids)

                # 返回结果

                return order

            # try:
            #     # 初始化生成订单基本信息表
            #     order = OrderInfo.objects.create(
            #         order_id=order_id,
            #         address=address,
            #         user=user,
            #         total_count=0,
            #         total_amount=Decimal(0),
            #         freight=Decimal(10),
            #         pay_method=pay_method,
            #         status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if
            #         pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']
            #         else OrderInfo.ORDER_STATUS_ENUM['UNPAID']
            #     )
            #     # 查询选中状态的SKU_id的sku商品
            #     conn = get_redis_connection('cart')
            #     # 3:获取选中状态的cku_id和count
            #
            #     sku_id_count = conn.hgetall('cart_%s' % user.id)  # 获取购物车中的商品对象,有count属性
            #     sku_ids = conn.smembers('cart_selected_%s' % user.id)  # 获取选中的商品id
            #     # 合并数据
            #     cart = {}
            #     for sku_id in sku_ids:
            #         cart[int(sku_id)] = int(sku_id_count[sku_id])
            #
            #     # 查询选中商品状态的对象,这个是去数据库中查询了
            #     skus = SKU.objects.filter(id__in=cart.keys())
            #     # 遍历所有sku商品
            #     for sku in skus:
            #
            #         # 获取当前sku商品原始库存和销量
            #         old_stock = sku.stock
            #         old_sales = sku.sales
            #         sku_count = cart[sku.id]
            #         # 判断购买数量是否大于库存
            #         if sku_count > old_stock:
            #             raise serializers.ValidationError('库存不足')
            #         # 不大于库存,则修改SKU商品的库存量和销量
            #         sku.stock = old_stock-sku_count
            #         sku.saled = old_sales+sku_count
            #         sku.save()
            #         # 修改SKU变中的销量
            #         sku.goods.sales += sku_count
            #         sku.goods.save()
            #         # 修改订单基本信息表中的总量和总价
            #         order.total_amount += (sku.price*sku_count)
            #         order.total_count += sku_count
            #         # 保存订单商品
            #         OrderGoods.objects.create(
            #             order = order,
            #             sku = sku,
            #             count = sku_count,
            #             price = sku.price
            #
            #         )
            #     #累加运费
            #     order.total_amount += order.freight
            #     order.save()




