import base64
import pickle

from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.
from carts.serializers import CartSerializers, SKUSerializers, CartDeleteSerializers, CartSelectSerializers
from goods.models import SKU


class CartsView(APIView):

    def perform_authentication(self, request):
        pass

    def post(self, request):

        """
                保存购物车
        :param request:
        :return:
        """
        # 1:获取前端数据
        data = request.data
        # 验证数据 >>>>序列化器
        ser = CartSerializers(data=data)
        ser.is_valid()
        print(ser.errors)

        sku_id = ser.validated_data['sku_id']
        count = ser.validated_data['count']
        selected = ser.validated_data['selected']

        try:
            user = request.user
        except:
            user = None

        if user is not None:
            # 1:建立缓存链接
            conn = get_redis_connection('cart')
            # 保存hash和set
            conn.hincrby('cart_%s' % user.id, sku_id, count)
            if selected:
                conn.sadd('cart_selected_%s' % user.id, sku_id)
            # 返回结果
            return Response('ok')

        else:
            # 先判断是否有cookie
            cart_cookie = request.COOKIES.get('cart_cookie')
            if cart_cookie:
                cart = pickle.loads(base64.b64decode(cart_cookie))
            else:
                cart = {}

            # 有cookie获取cookie值累加
            sku_dict = cart.get(sku_id)
            if sku_dict:
                count += int(sku_dict['count'])

            cart[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 将新的字典数据写入cookie
            response = Response('ok')
            # 加密写入的字典数据
            cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
            response.set_cookie('cart_cookie', cart_cookie, max_age=60 * 60 * 24 * 7)

            # 返回结果
            return response

    def get(self, request):

        """
                获取购物车
        :param request:
        :return:
        """
        try:
            user = request.user
        except:
            user = None

        if user is not None:
            # 1:建立缓存链接
            conn = get_redis_connection('cart')
            # 获取hash和set
            sku_id_count = conn.hgetall('cart_%s' % user.id)
            sku_selected = conn.smembers('cart_selected_%s' % user.id)
            # 转换为完整的购物车数据
            cart = {}
            for sku_id, count in sku_id_count.items():
                cart[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in sku_selected
                }


        else:
            # 先判断是否有cookie
            cart_cookie = request.COOKIES.get('cart_cookie')
            if cart_cookie:
                cart = pickle.loads(base64.b64decode(cart_cookie))
            else:
                cart = {}

        # 查询商品对象
        skus = SKU.objects.filter(id__in=cart.keys())

        for sku in skus:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']

        ser = SKUSerializers(skus, many=True)

        return Response(ser.data)

    def put(self, request):

        """
                修改购物车
        :param request:
        :return:
        """
        # 1:获取前端数据
        data = request.data
        # 验证数据 >>>>序列化器
        ser = CartSerializers(data=data)
        ser.is_valid()
        print(ser.errors)

        sku_id = ser.validated_data['sku_id']
        count = ser.validated_data['count']
        selected = ser.validated_data['selected']

        try:
            user = request.user
        except:
            user = None

        if user is not None:
            # 1:建立缓存链接
            conn = get_redis_connection('cart')
            # 更新hash和set
            conn.hset('cart_%s' % user.id, sku_id, count)
            if selected:
                conn.sadd('cart_selected_%s' % user.id, sku_id)

            else:
                conn.srem('cart_selected_%s' % user.id, sku_id)
            # 返回结果
            return Response(ser.data)

        else:
            # 先判断是否有cookie
            cart_cookie = request.COOKIES.get('cart_cookie')
            if cart_cookie:
                cart = pickle.loads(base64.b64decode(cart_cookie))
            else:
                cart = {}

            # 有cookie获取cookie值累加
            """
            更新数据不进行累加
            """
            # sku_dict = cart.get(sku_id)
            # if sku_dict:
            #     count += int(sku_dict['count'])

            cart[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 将新的字典数据写入cookie
            response = Response(ser.data)
            # 加密写入的字典数据
            cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
            response.set_cookie('cart_cookie', cart_cookie, max_age=60 * 60 * 24 * 7)

            # 返回结果
            return response

    def delete(self, request):

        """
                删除购物车
        :param request:
        :return:
        """
        # 1:获取前端数据
        data = request.data
        # 验证数据 >>>>序列化器
        ser = CartDeleteSerializers(data=data)
        ser.is_valid()
        print(ser.errors)

        sku_id = ser.validated_data['sku_id']


        try:
            user = request.user
        except:
            user = None

        if user is not None:
            # 1:建立缓存链接
            conn = get_redis_connection('cart')
            # 保存hash和set
            conn.hdel('cart_%s' % user.id, sku_id)
            conn.srem('cart_selected_%s' % user.id, sku_id)
            # 返回结果
            return Response('ok')

        else:
            # 先判断是否有cookie
            #生成相应对象
            response = Response('ok')
            cart_cookie = request.COOKIES.get('cart_cookie')
            if cart_cookie:
                cart = pickle.loads(base64.b64decode(cart_cookie))

            if sku_id in cart:
                del cart[sku_id]

                # 将新的字典数据写入cookie
                response = Response('ok')

                # 加密写入的字典数据
                cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
                response.set_cookie('cart_cookie', cart_cookie, max_age=60 * 60 * 24 * 7)

            # 返回结果
            return response


class CartSelectionView(APIView):

    def perform_authentication(self, request):
        pass

    def put(self, request):

        """
                全选购物车
        :param request:
        :return:
        """
        # 1:获取前端数据
        data = request.data
        # 验证数据 >>>>序列化器
        ser = CartSelectSerializers(data=data)
        ser.is_valid()
        print(ser.errors)

        selected = ser.validated_data['selected']

        try:
            user = request.user
        except:
            user = None

        if user is not None:
            # 1:建立缓存链接
            conn = get_redis_connection('cart')
            # 获取所有SKU_id值
            sku_id_count = conn.hgetall('cart_%s' % user.id)
            sku_ids = sku_id_count.keys()
            if selected:
                conn.sadd('cart_selected_%s' % user.id, *sku_ids)

            else:
                conn.srem('cart_selected_%s' % user.id, *sku_ids)
            # 返回结果
            return Response(ser.data)

        else:
            # 先判断是否有cookie
            response = Response(ser.data)

            cart_cookie = request.COOKIES.get('cart_cookie')
            if cart_cookie:
                cart = pickle.loads(base64.b64decode(cart_cookie))
                #更新字典中的选中状态
                for sku_id, data_dict in cart.items():
                    data_dict['selected'] = selected


            # 加密写入的字典数据
            cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
            response.set_cookie('cart_cookie', cart_cookie, max_age=60 * 60 * 24 * 7)

            # 返回结果
            return response